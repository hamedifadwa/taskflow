pipeline {
    agent any

    environment {
        PROJECT_DIR = "/workspace/taskflow"
        MONITOR_DIR = "/workspace/taskflow/monitor"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📥 Repository already available in mounted workspace"
                sh 'ls -R $PROJECT_DIR'
            }
        }

        stage('Debug Workspace') {
            steps {
                echo "🔍 Checking workspace structure..."
                sh '''
                    pwd
                    ls -l $PROJECT_DIR
                    ls -l $MONITOR_DIR
                    file $MONITOR_DIR/prometheus.yml
                '''
            }
        }

        stage('Stop Monitoring Stack') {
            steps {
                echo "🛑 Stopping monitoring stack..."
                sh '''
                    cd $MONITOR_DIR
                    docker-compose down
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
            echo "❌ Deployment failed - check logs"
        }
    }
}