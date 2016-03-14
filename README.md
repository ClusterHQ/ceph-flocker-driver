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

# Developer instructions

## Running the functional tests.

These instructions describe how to set up your development tree and run the functional tests from scratch.

They assume you already have the following installed:

- `git`
- `virtualenvwrapper`
- `pip`
- The development package requirements for flocker: `python-dev` `libffi-dev` `libssl-dev`
- A single node ceph cluster by following http://devcenter.megam.io/2015/03/27/ceph-in-a-single-node/


```bash
# Enter the directory that you want to check out deveopment trees into:
cd $PROJECTS_DIRECTORY  

# Clone this repository:
git clone https://github.com/ClusterHQ/ceph-flocker-driver.git

# Clone the flocker repository:
git clone https://github.com/ClusterHQ/flocker

# Enter the ceph repository:
cd ceph-flocker-driver

# Use a virtualenv for this package:
mkvirtualenv ceph-flocker-driver
workon ceph-flocker-driver

# Install flocker in the virtualenv:
pip install ../flocker

# Install development flocker dependencies in the virtualenv:
pip install -r ../flocker/dev-requirements.txt

# Install driver dependencies in the virtualenv:
pip install .
```
