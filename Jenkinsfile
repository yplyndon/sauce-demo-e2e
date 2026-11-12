pipeline {
  agent { docker { image 'python:3.12' args '-u root' } }
  options { timestamps() }
  parameters {
    choice(name: 'SUITE', choices: ['smoke', 'regression', 'api', 'e2e'], description: 'Marker to run')
    choice(name: 'BROWSER', choices: ['chromium', 'firefox', 'webkit'], description: 'Browser')
  }
  stages {
    stage('Install') {
      steps {
        sh 'pip install -r requirements.txt'
        sh 'playwright install --with-deps ${BROWSER}'
      }
    }
    stage('Test') {
      steps { sh 'pytest -m ${SUITE} --browser ${BROWSER} -n 4' }
    }
  }
  post {
    always { archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true }
  }
}
