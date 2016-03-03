"""
Provision ceph on a flocker acceptance test cluster.
"""

from effect import parallel
from effect.fold import sequence

from twisted.python.filepath import FilePath

from flocker.provision._ssh import run_remotely, run_from_args, put, run

from ._ssh import generate_rsa_key


def write_authorized_key(key):
    public_key_blob = key.public().toString("OPENSSH")
    return sequence([
        run_from_args([b"mkdir", b"-p", b".ssh"]),
        put(public_key_blob, b".ssh/ceph-deploy-key.pub"),
        run(
            b"if ! grep --quiet '{public_key}' .ssh/authorized_keys; then"
            b"  ("
            b"    echo; "
            b"    echo '# flocker-deploy access'; "
            b"    echo '{public_key}'; "
            b"  ) >> .ssh/authorized_keys; "
            b"fi; ".format(public_key=public_key_blob)
        ),
    ])


def write_ssh_key(key):
    public_key_blob = key.public().toString("OPENSSH")
    private_key_blob = key.toString('OPENSSH')
    return sequence([
        run_from_args([b"mkdir", b"-p", b".ssh"]),
        put(public_key_blob, ".ssh/id_rsa.pub"),
        put(private_key_blob, ".ssh/id_rsa"),
        run_from_args([b"chmod", b"u=rw,g=,o=", b".ssh/id_rsa"]),
    ])


def configure_ceph(cluster):
    """
    Provision ceph on a flocker acceptance test cluster.
    """

    key = generate_rsa_key()

    return sequence([
        parallel([
            run_remotely(
                username='root',
                address=node.address,
                commands=sequence([
                    write_authorized_key(key),
                    # XXX: Support ubuntu/fedora
                    run_from_args(['systemctl', 'enable', 'chronyd']),
                    run_from_args(['systemctl', 'restart', 'chronyd']),
                    run_from_args([
                        "/opt/flocker/bin/pip",
                        "install",
                        "https://github.com/ClusterHQ/ceph-flocker-driver"
                        "/archive/ceph-deploy.zip#egg-info=ceph_flocker_driver"
                    ]),
                ])
            )
            for node in cluster.all_nodes
        ]),
        run_remotely(
            username='root',
            address=cluster.control_node.address,
            commands=sequence([
                write_ssh_key(key),
                put(
                    FilePath(__file__).sibling('install-ceph.py').getContent(),
                    "/root/install-ceph.py",
                ),
                run_from_args(
                    ["/opt/flocker/bin/python", "/root/install-ceph.py"]
                    + [cluster.control_node.private_address]
                    + [node.private_address for node in cluster.agent_nodes]
                )
            ])
        ),
    ])
