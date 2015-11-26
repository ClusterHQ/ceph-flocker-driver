from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase

from ceph_rbd import CephRBDBlockDeviceAPI

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
        runner.add_command([b"rbd", b"showmapped"],
            'id pool       image            snap device    \n1  rbd        foo              -    /dev/rbd1 \n2  rbd        flocker-foo      -    /dev/rbd2 \n3  rbd        \xf0\x9f\x90\xb3             -    /dev/rbd3 \n4  other_pool some_other_image -    /dev/rbd4 \n')
        return api, runner

    def test_empty(self):
        """
        There are no maps, return an empty dict.
        """
        api, runner = self.get_api_and_runner()
        runner.add_command([b"rbd", b"showmapped"], "\n")
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
