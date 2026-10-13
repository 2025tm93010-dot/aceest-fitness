pipeline {
    agent any
    options { timestamps(); timeout(time: 15, unit: 'MINUTES') }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Clean Build (venv + lint)') {
            steps {
                sh '''
                    rm -rf .venv
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements-dev.txt
                    flake8 .
                '''
            }
        }
        stage('Unit Tests') {
            steps { sh '. .venv/bin/activate && pytest -v' }
        }
        stage('Docker Build') {
            steps {
                sh 'docker build --no-cache --target runtime -t aceest-fitness:${BUILD_NUMBER} .'
            }
        }
        stage('Docker Test') {
            steps {
                sh '''
                    docker build --target test -t aceest-fitness-test:${BUILD_NUMBER} .
                    docker run --rm aceest-fitness-test:${BUILD_NUMBER}
                '''
            }
        }
    }
    post {
        always { sh 'docker image prune -f || true' }
    }
}
