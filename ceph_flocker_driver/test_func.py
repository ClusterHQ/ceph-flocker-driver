"""
Minimal functional tests.
"""
from uuid import uuid4
from flocker.node.agents.test.test_blockdevice import (
    make_iblockdeviceapi_tests,
)
from ceph_flocker_driver.ceph_rbd import rbd_from_configuration


def api_factory(test_case):
    # Return an instance of your IBlockDeviceAPI implementation class, given
    # a twisted.trial.unittest.TestCase instance.
    return rbd_from_configuration("flocker", "ceph.admin", None, "rbd")

# Smallest volume to create in tests, e.g. 1GiB:
MIN_ALLOCATION_SIZE = 1024 * 1024 * 1024

# Minimal unit of volume allocation, e.g. 1MiB:
MIN_ALLOCATION_UNIT = 1024 * 1024


class YourStorageTests(make_iblockdeviceapi_tests(
    api_factory, MIN_ALLOCATION_SIZE, MIN_ALLOCATION_UNIT,
    # Factory for valid but unknown volume id specific to your backend:
    lambda test: unicode(uuid4()))
):
    """
    Tests for Ceph RBD driver.
    """
