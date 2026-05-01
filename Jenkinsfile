pipeline {
agent any

```
stages {

    stage('SCM') {
        steps {
            // Pull code from your repo
            checkout scm
        }
    }

    stage('Deploy (CD)') {
        steps {
            sh '''
            echo "Stopping existing containers..."
            docker-compose down

            echo "Starting containers..."
            docker-compose up -d
            '''
        }
    }

    stage('Monitor') {
        steps {
            sh '''
            echo "Checking running containers..."
            docker ps

            echo "Checking logs (last 20 lines)..."
            docker-compose logs --tail=20
            '''
        }
    }
}
```

}
