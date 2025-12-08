pipeline {
    agent any

    environment {
        IMAGE_NAME = "lms-app"
        CONTAINER_NAME = "lms-container"
        APP_PORT = "5000"
        AWS_REGION = 'us-east-1'  // adjust if needed
        SONAR_TOKEN = credentials('sonarqube-credentials')
    }
    stages {
        stage('Checkout Code') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-credentials', url: 'https://github.com/Wasiullah26/LMS-Learning-Management-System.git']])
            }
        }
        
        stage('Python Lint & Security Checks') {
    steps {
        echo "Running Pylint, Flake8, Bandit, Safety..."
        sh '''
            # Ensure Python 3 and pip are available
            python3 --version || exit 1
            python3 -m pip --version || exit 1

            # Create and activate virtual environment
            python3 -m venv venv
            . venv/bin/activate

            # Upgrade pip and install tools
            python3 -m pip install --upgrade pip
            python3 -m pip install pylint flake8 bandit safety

            # Run Pylint
            pylint backend/**/*.py || true

            # Run Flake8
            flake8 backend || true

            # Run Bandit (security checks)
            bandit -r backend -ll -iii || true

            # Run Safety (vulnerability scan)
            safety check || true
        '''
    }
}
stage('SonarQube Analysis') {
    steps {
        withSonarQubeEnv('SonarQube') {
            script {
                def scannerHome = tool 'sonar-scanner'
            }
            sh """
                ${tool('sonar-scanner')}/bin/sonar-scanner \
                  -Dsonar.projectKey=lms-project \
                  -Dsonar.sources=backend \
                  -Dsonar.exclusions=backend/venv/**,backend/__pycache__/**,backend/**/*.pyc,backend/reports/**,backend/.venv/**,frontend/node_modules/**,frontend/dist/**,frontend/build/**,frontend/reports/** \
                  -Dsonar.python.version=3 \
                  -Dsonar.host.url=http://34.232.240.118:9000 \
                  -Dsonar.login=${SONAR_TOKEN}
            """
        }
    }
}
        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Stop Existing Container') {
            steps {
                echo "Stopping existing container if running..."
                sh '''
                    if [ $(docker ps -q -f name=${CONTAINER_NAME}) ]; then
                        docker stop ${CONTAINER_NAME}
                        docker rm ${CONTAINER_NAME}
                    fi
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                echo "Running new container using EC2 IAM role..."
                sh """
                    docker run -d --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        -e AWS_REGION=${AWS_REGION} \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest
                """
            }
        }

        stage('Clean Up Old Docker Images') {
            steps {
                echo "Removing dangling Docker images..."
                sh "docker image prune -f"
            }
        }

        stage('Test DynamoDB Connectivity') {
            steps {
                echo "Testing DynamoDB access from container..."
                sh """
                    docker run --rm \
                        -e AWS_REGION=${AWS_REGION} \
                        ${IMAGE_NAME}:latest \
                        python -c "import boto3; list(boto3.resource('dynamodb', region_name='${AWS_REGION}').tables.all()); print('DynamoDB reachable')"
                """
            }
        }
    }

    post {
        success {
            echo "Deployment successful! App is running on port ${APP_PORT}"
        }
        failure {
            echo " Deployment failed!"
        }
    }
}
