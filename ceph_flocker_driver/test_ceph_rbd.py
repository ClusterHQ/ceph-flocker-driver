from os import environ
from uuid import uuid4
from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase, SkipTest

from ceph_rbd import CephRBDBlockDeviceAPI, rbd_from_configuration

from flocker.node.agents.blockdevice import AlreadyAttachedVolume
from flocker.node.agents.test.test_blockdevice import make_iblockdeviceapi_tests

class FakeCommandRunner(object):
    """
    Test helper to simulate ``subprocess.check_output``.
    """
    def __init__(self):
        self._outputs = dict()

    def add_command(self, command_spec, output):
        """
        Add a command output.

        :param list command_spec: A list of lists, the inner list is a command
            list which would be provided to ``check_output``.
        :param str output: The output of the command.
        """
        self._outputs[tuple(command_spec)] = output

    def check_output(self, command_spec):
        """
        Return the command output.

        :param list command_spec: A list of lists, the inner list is a command
            list which would be provided to ``check_output``.
        """
        return self._outputs[tuple(command_spec)]


class CephRBDBlockDeviceAPITests(TestCase):
    """
    Tests for ``CephRBDBlockDeviceAPI``.
    """
    def get_api_and_runner(self):
        runner = FakeCommandRunner()
        return (CephRBDBlockDeviceAPI(None, None, b"rbd", runner.check_output), runner)

    def _basic_output(self):
        """
        Get basic test api and runner.
        """
        api, runner = self.get_api_and_runner()
        runner.add_command([b"hostname", b"-s"], "ceph-node-1\n")
        runner.add_command([b"rbd", b"status", b"foo"],
                """Watchers:
    watcher=172.31.14.48:0/1953528273 client.5153 cookie=2\n""")
        runner.add_command([b"rbd", b"-p", b"rbd", b"showmapped"],
            'id pool       image            snap device    \n1  rbd        foo              -    /dev/rbd1 \n2  rbd        flocker-foo      -    /dev/rbd2 \n3  rbd        \xf0\x9f\x90\xb3             -    /dev/rbd3 \n4  other_pool some_other_image -    /dev/rbd4 \n')
        return api, runner

    def test_compute_instance_id(self):
        """
        The instance_id is the current node hostname.
        """
        api, runner = self._basic_output()
        self.assertEquals(api.compute_instance_id(), "ceph-node-1")

    def test_attach_already_attached(self):
        """
        ``attach_volume`` raises ``AlreadyAttachedVolume``.
        """
        api, runner = self._basic_output()
        self.assertRaises(AlreadyAttachedVolume, api.attach_volume, u"foo",
                api.compute_instance_id())


class ListMapsTests(TestCase):
    """
    Tests for ``CephRBDBlockDeviceAPI._list_maps``.
    """

    def get_api_and_runner(self):
        runner = FakeCommandRunner()
        return (CephRBDBlockDeviceAPI(None, None, b"rbd", runner.check_output), runner)

    def _basic_output(self):
        """
        Get basic test api and runner.
        """

        api, runner = self.get_api_and_runner()
        runner.add_command([b"rbd", b"-p", b"rbd", b"showmapped"],
            'id pool       image            snap device    \n1  rbd        foo              -    /dev/rbd1 \n2  rbd        flocker-foo      -    /dev/rbd2 \n3  rbd        \xf0\x9f\x90\xb3             -    /dev/rbd3 \n4  other_pool some_other_image -    /dev/rbd4 \n')
        return api, runner

    def test_empty(self):
        """
        There are no maps, return an empty dict.
        """
        api, runner = self.get_api_and_runner()
        runner.add_command([b"rbd", b"-p", b"rbd", b"showmapped"], "\n")
        maps = api._list_maps()
        self.assertEquals(maps, dict())

    def test_list_all(self):
        """
        Exactly the right list of mapped images.
        """
        api, runner = self._basic_output()
        maps = api._list_maps()
        images = maps.keys()
        self.assertEquals(images,
            [u'flocker-foo', u'foo', u'\U0001f433'])

    def test_list_bytes(self):
        """
        Images with ``bytes`` names are found.
        """
        api, runner = self._basic_output()
        maps = api._list_maps()
        self.assertEquals(maps[u"flocker-foo"], FilePath("/dev/rbd2"))

    def test_list_unicode(self):
        """
        Images with ``unicode`` names are found.
        """
        api, runner = self._basic_output()
        maps = api._list_maps()
        self.assertEquals(maps[u'\U0001f433'], FilePath("/dev/rbd3"))

    def test_foreign_pools_not_found(self):
        """
        Images in other pools are not found.
        """
        api, runner = self._basic_output()
        maps = api._list_maps()
        self.assertNotIn(u"other_pool", maps)


def api_factory(test_case):
    """
    :param test: A twisted.trial.unittest.TestCase instance
    """
    flocker_functional_test = environ.get('FLOCKER_FUNCTIONAL_TEST')
    if flocker_functional_test is None:
        raise SkipTest(
            'Please set FLOCKER_FUNCTIONAL_TEST environment variable to '
            'run storage backend functional tests.'
        )
    api = rbd_from_configuration("flocker", "client.admin", "/etc/ceph/ceph.conf", "rbd")
    test_case.addCleanup(api.destroy_all_flocker_volumes)
    return api


class CephRBDRealTests(make_iblockdeviceapi_tests(
    api_factory, 1024 * 1024 * 32, 1024 * 1024,
    lambda test: unicode(uuid4()))): # XXX this is a guess
    """
    Acceptance tests for the ceph_rbd driver.
    """
