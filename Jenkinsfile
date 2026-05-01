pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo "📥 Cloning repository..."
                checkout scm
            }
        }

        stage('stop container') {
            steps {
                echo "🚀 Stoping Monitor..."
                dir('monitor') {
                    sh 'docker-compose down'
            }
        }

        stage('Deploy Monitoring Stack') {
            steps {
                echo "📊 Deploying Monitoring..."
                dir('monitor') {
                    sh 'docker-compose up -d'
                }
            }
        }

    }

    post {
        success {
            echo "✅ Deployment successful"
        }

        failure {
            echo "❌ Deployment failed"
        }
    }
}