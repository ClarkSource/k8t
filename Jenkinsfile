pipeline {
  agent {
    kubernetes {
      defaultContainer 'jnlp'
      yamlFile '.jenkins/python.yaml'
    }
  }

  options {
    timeout(time: 2, unit: 'HOURS')
    timestamps()
    buildDiscarder(
      logRotator(
        daysToKeepStr: '14',
        numToKeepStr: '100',
        artifactDaysToKeepStr: '30',
      ))
  }

  stages {
    stage('setup') {
      steps {
        container('python') {
          sh 'pip install --upgrade tox'
        }
      }
    }

    stage('test') {
      steps {
        container('python') {
          sh 'tox'
        }
      }
    }
  }
}
