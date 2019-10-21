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

    stage('build') {
      when {
        branch 'master'
      }

      steps {
        sh 'pip install --upgrade setuptools wheel'
        sh 'python3 setup.py sdist bdist_wheel'
      }
    }

    stage('release') {
      when {
        buildingTag()
      }

      steps {
        sh 'pip install --upgrade twine'
        /* missing credentials
        sh 'twine upload dist/*'
        */
      }
    }
  }
}
