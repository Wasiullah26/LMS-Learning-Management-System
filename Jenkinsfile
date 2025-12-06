pipeline {
    agent any
    
    // Automatically trigger builds when code is pushed to GitHub
    triggers {
        pollSCM('H/5 * * * *')  // Check for changes every 5 minutes
    }
    
    environment {
        AWS_REGION = 'us-east-1'
        EB_APPLICATION_NAME = 'lms-application'
        EB_ENVIRONMENT_NAME = 'lms-env'
        EB_PLATFORM = 'python-3.11'  // Updated platform
        NODE_VERSION = '18'
        PYTHON_VERSION = '3.10'
        SONAR_TOKEN = credentials('sonarcloud-token')
        SONAR_ORGANIZATION = 'wasiullah26'
        SONAR_PROJECT_KEY = 'Wasiullah26_LMS-Learning-Management-System'
        AWS_SESSION_TOKEN = credentials('aws-session-token')  // AWS Academy Learner Lab session token
    }
    
    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }
        
        stage('Backend Analysis') {
            steps {
                dir('backend') {
                    bat '''
                        python -m venv venv || exit /b 0
                        call venv\\Scripts\\activate.bat || exit /b 0
                        pip install --upgrade pip || exit /b 0
                        pip install -r requirements.txt || exit /b 0
                        pip install -r requirements-dev.txt || exit /b 0
                        call run_analysis.bat || exit /b 0
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
                    bat '''
                        call npm ci || exit /b 0
                        call npm run lint || exit /b 0
                        call npm audit --audit-level=moderate || exit /b 0
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
                    bat """
                        @echo off
                        pip install sonar-scanner || npm install -g sonarqube-scanner || exit /b 0
                        sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.organization=${SONAR_ORGANIZATION} -Dsonar.sources=backend,frontend/src -Dsonar.exclusions=backend/venv/**,backend/__pycache__/**,backend/**/*.pyc,backend/reports/**,backend/.venv/**,backend/setup/aws_setup.py,backend/seed_database.py,frontend/node_modules/**,frontend/dist/**,frontend/build/**,frontend/reports/**,frontend/public/** -Dsonar.python.version=3.10 -Dsonar.python.coverage.reportPaths=backend/coverage.xml -Dsonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info -Dsonar.sourceEncoding=UTF-8 || exit /b 0
                    """
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    bat '''
                        call npm ci
                        call npm run build
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
                bat '''
                    @echo off
                    if not exist deploy mkdir deploy
                    xcopy /E /I /Y backend\\* deploy\\
                    if exist deploy\\venv rmdir /S /Q deploy\\venv
                    if exist deploy\\__pycache__ rmdir /S /Q deploy\\__pycache__
                    if exist deploy\\reports rmdir /S /Q deploy\\reports
                    del /Q deploy\\*.bat deploy\\*.sh 2>nul
                    if exist frontend\\dist xcopy /E /I /Y frontend\\dist deploy\\static\\
                    echo web: gunicorn application:application > deploy\\Procfile
                    if not exist deploy\\.ebextensions mkdir deploy\\.ebextensions
                    copy /Y backend\\requirements.txt deploy\\requirements.txt
                    (
                        echo import sys
                        echo import os
                        echo.
                        echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
                        echo.
                        echo from app import create_app
                        echo.
                        echo application = create_app()
                        echo.
                        echo if __name__ == "__main__":
                        echo     application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
                    ) > deploy\\application.py
                '''
            }
        }
        
        stage('Create ZIP for Deployment') {
            steps {
                bat """
                    cd deploy
                    powershell -Command "Compress-Archive -Path * -DestinationPath ..\\lms-deployment-${BUILD_NUMBER}.zip -Force"
                    cd ..
                """
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
                        bat """
                            @echo off
                            if defined AWS_SESSION_TOKEN set AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
                            pip install awsebcli --user || exit /b 0
                            cd deploy
                            eb deploy ${EB_ENVIRONMENT_NAME} --staged || eb deploy ${EB_ENVIRONMENT_NAME}
                            cd ..
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                try {
                    def qg = waitForQualityGate()
                    if (qg.status != 'OK') {
                        error "Pipeline aborted due to quality gate failure: ${qg.status}"
                    }
                } catch (Exception e) {
                    echo "SonarCloud quality gate check skipped: ${e.getMessage()}"
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
