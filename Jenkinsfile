pipeline {
  agent any
  options { timestamps(); timeout(time: 30, unit: 'MINUTES') }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Lint and Unit Tests') {
      steps {
        sh '''python3 -m venv .venv
          . .venv/bin/activate
          pip install -r requirements-dev.txt pytest-cov
          flake8 .
          pytest -v --cov=app --cov-report=xml:coverage.xml'''
      }
    }
    stage('SonarQube') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh 'sonar-scanner -Dsonar.projectKey=aceest-fitness -Dsonar.sources=. -Dsonar.tests=tests -Dsonar.python.coverage.reportPaths=coverage.xml'
        }
      }
    }
    stage('Docker Test and Build') {
      steps {
        sh '''docker build --target test -t aceest-fitness-test:${BUILD_NUMBER} .
          docker run --rm aceest-fitness-test:${BUILD_NUMBER}
          docker build --target runtime -t aceest-fitness:${BUILD_NUMBER} .'''
      }
    }
    stage('Push Docker Hub') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker tag aceest-fitness:${BUILD_NUMBER} "$DH_USER/aceest-fitness:${BUILD_NUMBER}"
            docker tag aceest-fitness:${BUILD_NUMBER} "$DH_USER/aceest-fitness:latest"
            docker push "$DH_USER/aceest-fitness:${BUILD_NUMBER}"
            docker push "$DH_USER/aceest-fitness:latest"
            docker logout'''
        }
      }
    }
    stage('Deploy Minikube') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''sed "s|DOCKERHUB_USERNAME|$DH_USER|g" k8s/base/deployment.yaml | kubectl apply -f -
            kubectl set image deployment/aceest-fitness app=$DH_USER/aceest-fitness:${BUILD_NUMBER}
            kubectl rollout status deployment/aceest-fitness --timeout=180s'''
        }
      }
    }
  }
  post { always { sh 'docker image prune -f || true' } }
}
