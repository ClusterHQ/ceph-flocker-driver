# Ceph RBD Plugin for ClusterHQ/flocker

This a Ceph Rados Block Device driver for Flocker, a container data orchestration system.

## Installation

Make sure you have the flocker node servies already installed. If not visit  [Install Flocker](https://docs.clusterhq.com/en/latest/installation/install-node.html)

**_Be sure to use /opt/flocker/bin/python as this will install the driver into the right python environment_**

Install using python
```bash
git clone https://github.com/ClusterHQ/flocker-ceph-driver
cd flocker-ceph-driver/
sudo /opt/flocker/bin/python setup.py install
```

**_Be sure to use /opt/flocker/bin/pip as this will install the driver into the right python environment_**

Install using pip
```
git clone https://github.com/ClusterHQ/flocker-ceph-driver
cd flocker-ceph-driver/
/opt/flocker/bin/pip install flocker-ceph-driver/
```

**Note:** Thank you for EMC for providing their ScaleIO driver on which this work was based: https://github.com/emccorp/scaleio-flocker-driver

# Development

This is sort of a destructive method for setting up an environment to run the functional tests.

It might be appropriate for developing on an ephemeral VM in a public cloud.

Set up a virtualenv that uses python binary in the flocker tree:
```bash
sudo /opt/flocker/bin/pip install virtualenvwrapper
mkdir ~/ceph-env
/opt/flocker/bin/virtualenv ~/ceph-env/
source ~/ceph-env/bin/activate
```

Install dependencies
```bash
```
