pipeline {
    agent any

    environment {
        BACKEND_DIR = "/workspace/taskflow/taskflow_backend_django"
        MONITOR_DIR = "/workspace/taskflow/taskflow_backend_django/monitor"
    }

    stages {

        stage('Debug Workspace') {
            steps {
                sh '''
                    pwd
                    ls -R /workspace/taskflow
                '''
            }
        }

        stage('Stop Monitoring Stack') {
            steps {
                echo "🛑 Stopping monitoring stack..."
                sh '''
                    cd $MONITOR_DIR
                    docker-compose down || true
                '''
            }
        }

        stage('Deploy Monitoring Stack') {
            steps {
                echo "📊 Deploying monitoring stack..."
                sh '''
                    cd $MONITOR_DIR
                    docker-compose up -d
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