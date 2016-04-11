# Ceph RBD Plugin for ClusterHQ/flocker

This a Ceph Rados Block Device driver for Flocker, a container data orchestration system.

# WARNING: THIS IS STILL IN DEVELOPMENT

ClusterHQ is working on this project right now, but it is not ready yet.
Thank you for your interest and watch out for a release!

## Installation

Make sure you have Flocker already installed. If not visit  [Install Flocker](https://docs.clusterhq.com/en/latest/using/installing/index.html)

**_Be sure to use /opt/flocker/bin/python as this will install the driver into the right python environment_**

Install using python
```bash
git clone https://github.com/ClusterHQ/flocker-ceph-driver
cd flocker-ceph-driver/
sudo /opt/flocker/bin/python setup.py install
```

**_Be sure to use /opt/flocker/bin/pip as this will install the driver into the right python environment_**

Install using pip
```bash
git clone https://github.com/ClusterHQ/flocker-ceph-driver
cd flocker-ceph-driver/
/opt/flocker/bin/pip install flocker-ceph-driver/
```

**Note:** Thank you for EMC for providing their ScaleIO driver on which this work was based: https://github.com/emccorp/scaleio-flocker-driver

## Configuration

Reminder that this project is still under development, but if you want to
install and use it from the master branch, do the following:

On every agent node you need to install this driver into the python environment
in which flocker runs:

```bash
/opt/flocker/bin/pip install git+https://github.com/ClusterHQ/ceph-flocker-driver.git@master
```

Then you need to set up your `agent.yml` to be configured to use this driver:


```yaml
version: 1
  control-service:
    hostname: "user.controlserver.example.com"
  dataset:
    backend: "ceph_flocker_driver"
    cluster_name: "Ceph cluster name, defaults to ''"
    user_id: "Ceph user ID, defaults to 'admin'"
    ceph_conf_path: "path to ceph conf for rados, defaults to '/etc/ceph/ceph.conf'"
    storage_pool: "name of storage pool to use, defaults to 'rbd'"
```
