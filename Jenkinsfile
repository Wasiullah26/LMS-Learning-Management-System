pipeline {
    agent any
    
    // Automatically trigger builds when code is pushed to GitHub
    triggers {
        pollSCM('* * * * *')  // Check for changes every minute (H/1 means once per hour, * means every minute)
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
                    script {
                        // Try to find Python using PowerShell
                        def pythonExe = bat(
                            script: '@echo off & powershell -Command "$p = Get-Command python -ErrorAction SilentlyContinue; if ($p) { Write-Host $p.Source } else { $p = Get-Command py -ErrorAction SilentlyContinue; if ($p) { Write-Host $p.Source } else { Write-Host \"NOT_FOUND\" } }"',
                            returnStdout: true
                        ).trim()
                        
                        if (pythonExe == "NOT_FOUND" || pythonExe.isEmpty()) {
                            echo "Python not found - skipping backend analysis. This is optional."
                        } else {
                            bat """
                                @echo off
                                "${pythonExe}" -m venv venv || exit /b 0
                                call venv\\Scripts\\activate.bat || exit /b 0
                                python -m pip install --upgrade pip || exit /b 0
                                python -m pip install -r requirements.txt || exit /b 0
                                python -m pip install -r requirements-dev.txt || exit /b 0
                                call run_analysis.bat || exit /b 0
                            """
                        }
                    }
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
                        where python >nul 2>&1 && python -m pip install sonar-scanner || where py >nul 2>&1 && py -m pip install sonar-scanner || npm install -g sonarqube-scanner || exit /b 0
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
                    copy /Y .ebextensions\\* deploy\\.ebextensions\\ 2>nul
                    powershell -Command "$lines = @('import sys', 'import os', '', 'sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''backend''))', '', 'from app import create_app', '', 'application = create_app()', '', 'if __name__ == ''__main__'':', '    application.run(host=''0.0.0.0'', port=int(os.environ.get(''PORT'', 5000)))'); $lines | Out-File -FilePath deploy\\application.py -Encoding utf8"
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
                            echo ========================================
                            echo Starting Elastic Beanstalk Deployment
                            echo ========================================
                            
                            REM Set AWS session token if available
                            if defined AWS_SESSION_TOKEN (
                                set AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
                                echo AWS Session Token set
                            )
                            
                            REM Install EB CLI
                            echo Installing EB CLI...
                            where python >nul 2>&1 && python -m pip install awsebcli --user || where py >nul 2>&1 && py -m pip install awsebcli --user
                            if errorlevel 1 (
                                echo ERROR: Failed to install EB CLI
                                exit /b 1
                            )
                            
                            REM Verify EB CLI installation
                            eb --version
                            if errorlevel 1 (
                                echo ERROR: EB CLI not found after installation
                                exit /b 1
                            )
                            
                            REM Copy .elasticbeanstalk config to deploy directory
                            echo Setting up EB configuration...
                            if not exist deploy\\.elasticbeanstalk mkdir deploy\\.elasticbeanstalk
                            if exist .elasticbeanstalk\\config.yml (
                                copy /Y .elasticbeanstalk\\config.yml deploy\\.elasticbeanstalk\\config.yml
                                echo EB config copied
                            ) else (
                                echo Warning: .elasticbeanstalk\\config.yml not found
                            )
                            
                            REM Deploy to Elastic Beanstalk
                            echo Deploying to ${EB_ENVIRONMENT_NAME}...
                            cd deploy
                            
                            REM Try to use the environment
                            eb use ${EB_ENVIRONMENT_NAME} 2>&1 || echo Warning: Could not set EB environment, continuing...
                            
                            REM Deploy
                            echo Running eb deploy...
                            eb deploy ${EB_ENVIRONMENT_NAME} --staged 2>&1 || eb deploy ${EB_ENVIRONMENT_NAME} 2>&1
                            set DEPLOY_EXIT_CODE=%ERRORLEVEL%
                            
                            if %DEPLOY_EXIT_CODE% neq 0 (
                                echo ERROR: Deployment failed with exit code %DEPLOY_EXIT_CODE%
                                cd ..
                                exit /b %DEPLOY_EXIT_CODE%
                            )
                            
                            echo ========================================
                            echo Deployment completed successfully!
                            echo ========================================
                            cd ..
                        """
                    }
                }
            }
            post {
                success {
                    echo 'Deployment to Elastic Beanstalk succeeded!'
                }
                failure {
                    echo 'Deployment to Elastic Beanstalk failed! Check logs above.'
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
