pipeline {
  agent {
    kubernetes {
      defaultContainer 'python'
      yamlFile '.jenkins/python.yaml'
    }
  }

  options {
    timeout(time: 2, unit: 'HOURS')
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
        sh 'pip install --upgrade tox'
      }
    }

    stage('test') {
      steps {
        sh 'tox'
      }
    }
  }
}
