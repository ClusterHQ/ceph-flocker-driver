from setuptools import setup, find_packages
import codecs  # To use a consistent encoding

# Get the long description from the relevant file
with codecs.open('DESCRIPTION.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ceph_flocker_driver',
    version='0.1',
    description='Ceph RBD driver for ClusterHQ/Flocker',
    long_description=long_description,
    author='ClusterHQ Team',
    author_email='support@clusterhq.com',
    url='https://github.com/ClusterHQ/flocker-ceph-driver',
    license='Apache 2.0',

    keywords='backend, plugin, flocker, docker, python',
    packages=find_packages(exclude=['test*']),
    install_requires=['python-cephlibs'],
)
