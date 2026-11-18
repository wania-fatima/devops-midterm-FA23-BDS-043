pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  triggers { githubPush() }
  environment {
    IMAGE = 'midterm-api'
    CONTAINER = 'midterm-api'
  }
  stages {
    stage('Fetch latest data') {
      steps {
        sh 'git log -1 --oneline && wc -l dataset/train.csv'
      }
    }
    stage('Retrain model') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -q -r requirements.txt pytest httpx
          python train.py
        '''
      }
    }
    stage('Test') {
      steps {
        sh '. .venv/bin/activate && python -m pytest -q'
      }
    }
    stage('Build Docker image') {
      steps {
        sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .'
      }
    }
    stage('Deploy on EC2') {
      steps {
        sh '''
          docker rm -f ${CONTAINER} || true
          docker run -d --name ${CONTAINER} --restart unless-stopped -p 8000:8000 ${IMAGE}:latest
          for i in $(seq 1 20); do
            if curl -fs http://localhost:8000/metrics; then echo; docker image prune -f; exit 0; fi
            sleep 3
          done
          echo "App did not come up"; docker logs ${CONTAINER}; exit 1
        '''
      }
    }
  }
  post {
    always {
      withCredentials([usernamePassword(credentialsId: 'gmail-smtp', usernameVariable: 'SMTP_USER', passwordVariable: 'SMTP_PASS')]) {
        sh "python3 send_email.py ${currentBuild.currentResult}"
      }
    }
  }
}
