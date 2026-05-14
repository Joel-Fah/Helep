pipeline {
  agent any

  triggers {
    pollSCM('H/2 * * * *')
  }

  parameters {
    booleanParam(
      name: 'DEPLOY_TO_MINIKUBE',
      defaultValue: false,
      description: 'Deploy the Helm chart to the local Minikube cluster after validation.'
    )
  }

  environment {
    IMAGE_TAG = "jenkins-${BUILD_NUMBER}"
  }

  stages {
    stage('Tool Versions') {
      steps {
        bat 'git --version'
        bat 'docker --version'
        bat 'kubectl version --client=true'
        bat 'helm version'
        bat 'docker run --rm python:3.12-slim python --version'
      }
    }

    stage('Python Syntax Checks') {
      steps {
        bat 'docker run --rm -v "%CD%":/workspace -w /workspace python:3.12-slim python -m py_compile services/user-service/app/main.py services/user-service/app/db.py services/user-service/app/events.py'
        bat 'docker run --rm -v "%CD%":/workspace -w /workspace python:3.12-slim python -m py_compile services/sos-service/app/main.py services/sos-service/app/db.py services/sos-service/app/events.py'
        bat 'docker run --rm -v "%CD%":/workspace -w /workspace python:3.12-slim python -m py_compile services/dispatch-service/app/main.py services/dispatch-service/app/db.py services/dispatch-service/app/events.py services/dispatch-service/app/matching.py'
        bat 'docker run --rm -v "%CD%":/workspace -w /workspace python:3.12-slim python -m py_compile services/notification-service/app/main.py services/notification-service/app/db.py services/notification-service/app/events.py'
        bat 'docker run --rm -v "%CD%":/workspace -w /workspace python:3.12-slim python -m py_compile services/analytics-service/app/main.py services/analytics-service/app/db.py services/analytics-service/app/events.py'
      }
    }

    stage('Docker Build') {
      steps {
        bat 'docker build -t helep/user-service:%IMAGE_TAG% services/user-service'
        bat 'docker build -t helep/sos-service:%IMAGE_TAG% services/sos-service'
        bat 'docker build -t helep/dispatch-service:%IMAGE_TAG% services/dispatch-service'
        bat 'docker build -t helep/notification-service:%IMAGE_TAG% services/notification-service'
        bat 'docker build -t helep/analytics-service:%IMAGE_TAG% services/analytics-service'
      }
    }

    stage('Helm Validate') {
      steps {
        bat 'helm lint charts/helep'
        bat 'helm template helep charts/helep'
      }
    }

    stage('Optional Minikube Deploy') {
      when {
        expression { return params.DEPLOY_TO_MINIKUBE }
      }
      steps {
        bat 'helm upgrade --install helep charts/helep -n helep --create-namespace'
        bat 'kubectl get pods -n helep'
        bat 'kubectl get svc -n helep'
      }
    }
  }

  post {
    success {
      echo 'HELEP CI pipeline completed successfully.'
    }
    failure {
      echo 'HELEP CI pipeline failed. Check the failed stage and console output.'
    }
    always {
      echo "Build tag used: ${IMAGE_TAG}"
    }
  }
}
