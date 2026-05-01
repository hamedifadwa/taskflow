pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo "📥 Cloning repository..."
                checkout scm
            }
        }

        stage('Debug') {
            steps {
                sh 'pwd'
                sh 'ls -R'
            }
        }

        stage('Stop container') {
            steps {
                echo "🚀 Stopping Monitor..."
                sh 'docker-compose -f monitor/docker-compose.yml down'
            }
        }

        stage('Deploy Monitoring Stack') {
            steps {
                echo "📊 Deploying Monitoring..."
                sh 'docker-compose -f monitor/docker-compose.yml up -d'
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