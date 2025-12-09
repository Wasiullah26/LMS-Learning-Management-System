pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'  // Change to your region
        EB_APPLICATION_NAME = 'lms-application'
        EB_ENVIRONMENT_NAME = 'lms-env'
        EB_PLATFORM = 'Python 3.10'
        NODE_VERSION = '18'
        PYTHON_VERSION = '3.10'
        SONAR_TOKEN = credentials('sonarcloud-token')  // Jenkins credential ID
        SONAR_ORGANIZATION = 'wasiullah26'  // Your SonarCloud organization key
        SONAR_PROJECT_KEY = 'Wasiullah26_LMS-Learning-Management-System'  // Your SonarCloud project key (single project for whole repo)
        AWS_SESSION_TOKEN = credentials('aws-session-token')  // AWS Academy Learner Lab session token (optional - only needed for temporary credentials)
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Backend Analysis') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv venv || true
                        source venv/bin/activate || . venv/Scripts/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install -r requirements-dev.txt
                        ./run_analysis.sh || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'backend/reports/*.txt', allowEmptyArchive: true
                }
            }
        }
        
        stage('Frontend Analysis') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci
                        npm run lint || true
                        npm audit --audit-level=moderate || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'frontend/reports/*.txt', allowEmptyArchive: true
                }
            }
        }
        
        stage('SonarCloud Analysis') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh '''
                        # Install SonarScanner
                        pip install sonar-scanner || pip3 install sonar-scanner || npm install -g sonarqube-scanner || true
                        
                        # Run SonarScanner from root directory (analyzes both backend and frontend)
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.organization=${SONAR_ORGANIZATION} \
                            -Dsonar.sources=backend,frontend/src \
                            -Dsonar.exclusions=backend/venv/**,backend/__pycache__/**,backend/**/*.pyc,backend/reports/**,backend/.venv/**,backend/setup/aws_setup.py,backend/seed_database.py,frontend/node_modules/**,frontend/dist/**,frontend/build/**,frontend/reports/**,frontend/public/** \
                            -Dsonar.python.version=3.10 \
                            -Dsonar.python.coverage.reportPaths=backend/coverage.xml \
                            -Dsonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info \
                            -Dsonar.sourceEncoding=UTF-8
                    '''
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci
                        npm run build
                    '''
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'frontend/dist/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Prepare Deployment Package') {
            steps {
                sh '''
                    # Create deployment directory
                    mkdir -p deploy
                    
                    # Copy backend files
                    cp -r backend/* deploy/
                    rm -rf deploy/venv deploy/__pycache__ deploy/reports
                    rm -f deploy/*.bat deploy/*.sh
                    
                    # Copy frontend build
                    cp -r frontend/dist deploy/static
                    
                    # Create Procfile for Elastic Beanstalk
                    echo "web: gunicorn application:application" > deploy/Procfile
                    
                    # Create .ebextensions directory
                    mkdir -p deploy/.ebextensions
                    
                    # Create requirements.txt in root (EB expects it)
                    cp backend/requirements.txt deploy/requirements.txt
                    
                    # Create application.py (EB entry point)
                    cat > deploy/application.py << 'EOF'
from app import create_app
import os

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
EOF
                '''
            }
        }
        
        stage('Create ZIP for Deployment') {
            steps {
                sh '''
                    cd deploy
                    zip -r ../lms-deployment-${BUILD_NUMBER}.zip .
                    cd ..
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'lms-deployment-*.zip', allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy to Elastic Beanstalk') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                        sh '''
                            # Set session token for temporary credentials (AWS Academy Learner Lab)
                            # This is only needed if using temporary credentials with session tokens
                            if [ -n "${AWS_SESSION_TOKEN}" ]; then
                                export AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN}"
                            fi
                            
                            # Install EB CLI if not present
                            pip3 install awsebcli --user || true
                            
                            # Deploy using EB CLI
                            cd deploy
                            eb deploy "${EB_ENVIRONMENT_NAME}" --staged || eb deploy "${EB_ENVIRONMENT_NAME}"
                            cd ..
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Wait for SonarCloud quality gate
            script {
                def qg = waitForQualityGate()
                if (qg.status != 'OK') {
                    error "Pipeline aborted due to quality gate failure: ${qg.status}"
                }
            }
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}


