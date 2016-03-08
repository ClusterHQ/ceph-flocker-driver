// vim: ai ts=2 sts=2 et sw=2 ft=groovy et

def acceptance_artifacts = [
  "trial.log",
  "results.xml",
  "run-acceptance-tests.log",
  "_trial/test.log",
  "remote_logs.log",
]

def archive_list(artifacts) {
   for (int i = 0; i < artifacts.size(); i++) {
     archive artifacts[i]
   }
}

def subunit_results(file) {
  // subunit2junitxml exits non-zero if there are failing tests
  sh "cat ${file} | subunit-1to2 | subunit2junitxml --no-passthrough --output-to=results.xml || true"
  step([$class: 'JUnitResultArchiver', testResults: '**/results.xml'])
}

node ("aws-centos-7-SELinux-T2Medium"){
  wrap([$class: 'TimestamperBuildWrapper']) {
     echo "Checking out source."
     checkout scm
     dir ("flocker") {
       git url:'https://github.com/ClusterHQ/flocker.git', branch:'tp-test'
     }
     echo "Creating virtualenv."
     def venv = "${pwd()}/v"
     sh "rm -rf ${venv}"
     sh "virtualenv ${venv}"
     withEnv(["PATH+VENV=${venv}/bin"]) {
       sh "${venv}/bin/pip install . ./flocker[dev]  python-subunit junitxml --process-dependency-links"
       sh 'touch ${HOME}/.ssh/known_hosts'
       echo "Running tests."
       try {
         sshagent(['af3d96ee-5398-41ee-a8b4-b59cb071fa5a']) {
           sh "${venv}/bin/python flocker/admin/run-acceptance-tests --distribution centos-7 --provider aws --config-file /tmp/acceptance.yaml --branch master --dataset-backend ceph_flocker_driver -- --reporter=subunit flocker.acceptance 2>&1 | tee trial.log"
         }
       } finally {
         echo "Collecting Results."
         archive_list(acceptance_artifacts)
         subunit_results("trial.log")
       }
     }
  }
}
