"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
from uuid import UUID
import logging
import requests
import json
import rados
import rbd

from subprocess import check_output

from bitmath import Byte, GiB, MiB, KiB

from scaleiopy import ScaleIO

from eliot import Message, Logger
from zope.interface import implementer, Interface
from twisted.python.filepath import FilePath
from characteristic import attributes

from flocker.node.agents.blockdevice import (
    AlreadyAttachedVolume, IBlockDeviceAPI,
    BlockDeviceVolume, UnknownVolume, UnattachedVolume
)

_logger = Logger()

DEFAULT_CLUSTER_NAME = ""

# All Ceph clusters have a user "client.admin"
DEFAULT_USER_ID = "admin"

# On a freshly installed cluster, only the rbd pool exists.
DEFAULT_STORAGE_POOL = "rbd"

# We will look for ceph.conf in /etc/ceph
DEFAULT_CEPF_CONF_PATH = "/etc/ceph/ceph.conf"

class ImageExists(Exception):
    """
    An RBD image with the requested image name already exists.
    """
    def __init__(self, blockdevice_id):
        Exception.__init__(self, blockdevice_id)
        self.blockdevice_id = blockdevice_id

def finally_shutdown(func):
    """
    Decorator to shutdown any connection after it has been used.
    """
    def wrap(self, *args, **kwargs):
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            self.shutdown()
            raise e
        else:
            self.shutdown()
            return value
    return wrap

def _blockdevice_id(dataset_id):
    return "flocker-%s" % (dataset_id,)

def _dataset_id(blockdevice_id):
    return blockdevice_id[8:]

@implementer(IBlockDeviceAPI)
class CephRBDBlockDeviceAPI(object):
    """
    A ``IBlockDeviceAPI`` which uses Ceph Rados Block Devices.
    """

    def __init__(self, connection, ioctx, pool, command_runner):
        """
        XXX TODO
        """
        self._connection = connection
        self._ioctx = ioctx
        self._pool = pool
        self._check_output = command_runner

    def _check_exists(self, blockdevice_id):
        """
        Check if the image indicated by ``blockdevice_id`` already exists, and
        raise ``UnknownVolume`` if so.
        """
        rbd_inst = rbd.RBD()
        all_images = rbd_inst.list(self._ioctx)
        if blockdevice_id not in all_images:
            raise UnknownVolume(blockdevice_id)

    def _list_maps(self):
        """
        Return a ``dict`` mapping unicode RBD image names to mounted block
        device ``FilePath``s.
        """
        maps = dict()
        showmapped_output = self._check_output([b"rbd", b"showmapped"])
        if not len(showmapped_output):
            return maps
        lines = showmapped_output.split(b"\n")
        if len(lines) == 1:
            raise Exception("Unexpecetd `rbd showmapped` output: %r" % (showmapped_output,))
        lines.pop(0)
        for line in lines.split():
            image_id, pool, image_name, snap, mountpoint = line
            if pool != self._pool:
                continue
            maps[unicode(image_name)] = FilePath(mountpoint)
        return maps

    @finally_shutdown
    def create_volume(self, dataset_id, size):
        """
        Create a new volume as an RBD image.

        :param UUID dataset_id: The Flocker dataset ID of the dataset on this
            volume.
        :param int size: The size of the new volume in bytes.
        :returns: A ``BlockDeviceVolume``.
        """
        blockdevice_id = _blockdevice_id(dataset_id)
        rbd_inst = rbd.RBD()
        all_images = rbd_inst.list(self._ioctx)
        if blockdevice_id in all_images:
            raise ImageExists(blockdevice_id)
        rbd_inst.create(self._ioctx, blockdevice_id, size)
        return BlockDeviceVolume(blockdevice_id, size, None, dataset_id)

    @finally_shutdown
    def destroy_volume(self, blockdevice_id):
        """
        Destroy an existing RBD image.

        :param unicode blockdevice_id: The unique identifier for the volume to
            destroy.
        :raises UnknownVolume: If the supplied ``blockdevice_id`` does not
            exist.
        :return: ``None``
        """
        self._check_exists(blockdevice_id)
        rbd_inst = rbd.RBD()
        rbd_inst.remove(self._ioctx, blockdevice_id)

    @finally_shutdown
    def attach_volume(self, blockdevice_id, attach_to):
        """
        Attach ``blockdevice_id`` to the node indicated by ``attach_to``.

        :param unicode blockdevice_id: The unique identifier for the block
            device being attached.
        :param unicode attach_to: An identifier like the one returned by the
            ``compute_instance_id`` method indicating the node to which to
            attach the volume.

        :raises UnknownVolume: If the supplied ``blockdevice_id`` does not
            exist.
        :raises AlreadyAttachedVolume: If the supplied ``blockdevice_id`` is
            already attached.
        :returns: A ``BlockDeviceVolume`` with a ``attached_to`` attribute set
            to ``attach_to``.
        """
        if attach_to != self.compute_instance_id():
            # TODO log this.
            return
        self._check_exists(blockdevice_id)
        maps = self._list_maps()
        if blockdevice_id in maps:
            raise AlreadyAttachedVolume(blockdevice_id)

        self._check_output([b"rbd", b"map", blockdevice_id]).strip()

        rbd_image = rbd.Image(self._ioctx, blockdevice_id)
        size = rbd_image.stat()["size"]
        return BlockDeviceVolume(blockdevice_id, size, self.compute_instance_id(), _dataset_id(blockdevice_id))


    def shutdown(self):
        """
        Close and shut down the Ceph connection.
        """
        self._ioctx.close()
        self._connection.close()

def rbd_from_configuration(cluster_name, user_id, ceph_conf_path, storage_pool):
    try:
        cluster = rados.Rados(conffile=ceph_conf_path)
    except TypeError as e:
        # XXX eliot
        raise e

    try:
        cluster.connect()
    except Exception as e:
        # XXX eliot
        raise e

    if not cluster.pool_exists(storage_pool):
        raise Exception("Pool does not exist") # XXX eliot
    ioctx = cluster.open_ioctx(storage_pool)

    return CephRBDBlockDeviceAPI(cluster, ioctx, storage_pool, check_output)
