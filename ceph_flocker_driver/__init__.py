"""
Ceph driver for Flocker.
"""

from flocker.node import BackendDescription, DeployerType
from .ceph_rbd import (
    rbd_from_configuration, DEFAULT_CLUSTER_NAME, DEFAULT_USER_ID,
    DEFAULT_CEPF_CONF_PATH, DEFAULT_STORAGE_POOL
)


def api_factory(cluster_id, test_case=None, **kwargs):
    """
    Create a ``IBlockDeviceAPI`` for ceph.
    """
    cluster_name = DEFAULT_CLUSTER_NAME
    if "cluster_name" in kwargs:
        cluster_name = kwargs["cluster_name"]

    user_id = DEFAULT_USER_ID
    if "user_id" in kwargs:
        user_id = kwargs["user_id"]

    ceph_conf_path = DEFAULT_CEPF_CONF_PATH
    if "ceph_conf_path" in kwargs:
        ceph_conf_path = kwargs["ceph_conf_path"]

    storage_pool = DEFAULT_STORAGE_POOL
    if "storage_pool" in kwargs:
        storage_pool = kwargs["storage_pool"]

    return rbd_from_configuration(
        cluster_name=cluster_name, user_id=user_id,
        ceph_conf_path=ceph_conf_path, storage_pool=storage_pool)


def configure_cluster(cluster):
    from .provision import configure_ceph
    return configure_ceph(cluster)

FLOCKER_BACKEND = BackendDescription(
    name=u"ceph_flocker_driver",
    needs_reactor=False, needs_cluster_id=True,
    api_factory=api_factory, deployer_type=DeployerType.block,
    acceptance_configure_cluster=configure_cluster,
)
