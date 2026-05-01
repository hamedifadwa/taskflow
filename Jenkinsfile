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
                dir('monitor') {
                    sh 'docker-compose down'
                }
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