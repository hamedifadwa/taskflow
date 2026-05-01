pipeline {
    agent any

    stages {

        stage('Checkout SCM') {
            steps {
                echo "📥 Pulling latest code from repository..."
                checkout scm
            }
        }

        stage('Stop Monitoring Stack') {
            steps {
                echo "🛑 Stopping monitoring stack..."
                sh '''
                    docker compose -f /home/user/taskflow/taskflow_backend_django/monitor/docker-compose.yml down || true
                '''
            }
        }

        stage('Deploy Monitoring Stack') {
            steps {
                echo "📊 Deploying monitoring stack..."
                sh '''
                    docker compose -f /home/user/taskflow/taskflow_backend_django/monitor/docker-compose.yml up -d
                '''
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