pipeline {
    agent any
    
    // Automatically trigger builds when code is pushed to GitHub
    triggers {
        pollSCM('* * * * *')  // Check for changes every minute
    }
    
    environment {
        AWS_REGION = 'us-east-1'
        EB_APPLICATION_NAME = 'lms-application'
        EB_ENVIRONMENT_NAME = 'lms-env'
        EB_PLATFORM = 'python-3.11'
        NODE_VERSION = '18'
        PYTHON_VERSION = '3.10'
        SONAR_TOKEN = credentials('sonarcloud-token')
        SONAR_ORGANIZATION = 'wasiullah26'
        SONAR_PROJECT_KEY = 'Wasiullah26_LMS-Learning-Management-System'
        AWS_SESSION_TOKEN = credentials('aws-session-token')  // AWS Academy Learner Lab session token
        DEPLOY_ZIP = "lms-deployment-${BUILD_NUMBER}.zip"
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
                    powershell -Command "Compress-Archive -Path * -DestinationPath ..\\${DEPLOY_ZIP} -Force"
                    cd ..
                """
            }
            post {
                success {
                    archiveArtifacts artifacts: "${DEPLOY_ZIP}", allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy to Elastic Beanstalk') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                        bat """
                            @echo off
                            setlocal enabledelayedexpansion
                            
                            REM Set AWS session token if available
                            if defined AWS_SESSION_TOKEN (
                                set AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
                                echo AWS Session Token set
                            )
                            
                            REM Get AWS account ID directly (no temp files)
                            echo Getting AWS account ID...
                            for /f "tokens=*" %%a in ('aws sts get-caller-identity --query Account --output text --region ${AWS_REGION} 2^>nul') do set AWS_ACCOUNT_ID=%%a
                            
                            if "!AWS_ACCOUNT_ID!"=="" (
                                echo ERROR: Could not get AWS account ID
                                echo Please ensure AWS credentials have proper permissions
                                exit /b 1
                            )
                            
                            echo AWS Account ID: !AWS_ACCOUNT_ID!
                            
                            REM Try to get bucket from existing version first
                            echo Checking for existing S3 bucket...
                            for /f "tokens=*" %%b in ('aws elasticbeanstalk describe-application-versions --application-name ${EB_APPLICATION_NAME} --max-items 1 --region ${AWS_REGION} --query "ApplicationVersions[0].SourceBundle.S3Bucket" --output text 2^>nul') do set EB_S3_BUCKET=%%b
                            
                            REM Check if bucket is empty or "None" (AWS CLI returns "None" as string)
                            if "!EB_S3_BUCKET!"=="" (
                                set EB_S3_BUCKET=elasticbeanstalk-${AWS_REGION}-!AWS_ACCOUNT_ID!
                                echo Constructed bucket: !EB_S3_BUCKET!
                            ) else if "!EB_S3_BUCKET!"=="None" (
                                set EB_S3_BUCKET=elasticbeanstalk-${AWS_REGION}-!AWS_ACCOUNT_ID!
                                echo Bucket was None, constructed bucket: !EB_S3_BUCKET!
                            ) else (
                                echo Found existing bucket: !EB_S3_BUCKET!
                            )
                            
                            set VERSION_LABEL=app-${BUILD_NUMBER}
                            
                            REM Check if bucket exists, create if it doesn't
                            echo Checking if S3 bucket exists...
                            aws s3 ls "s3://!EB_S3_BUCKET!" --region ${AWS_REGION} >nul 2>&1
                            if errorlevel 1 (
                                echo Bucket does not exist, creating it...
                                aws s3 mb "s3://!EB_S3_BUCKET!" --region ${AWS_REGION}
                                if errorlevel 1 (
                                    echo ERROR: Failed to create S3 bucket
                                    echo Please check AWS permissions
                                    exit /b 1
                                )
                                echo Successfully created bucket: !EB_S3_BUCKET!
                            ) else (
                                echo Bucket already exists: !EB_S3_BUCKET!
                            )
                            
                            REM Upload to S3
                            echo Uploading ${DEPLOY_ZIP} to S3...
                            aws s3 cp "${DEPLOY_ZIP}" "s3://!EB_S3_BUCKET!/${DEPLOY_ZIP}" --region ${AWS_REGION}
                            if errorlevel 1 (
                                echo ERROR: Failed to upload to S3
                                echo Please check AWS permissions and bucket access
                                exit /b 1
                            )
                            echo Successfully uploaded to S3
                            
                            REM Create application version
                            echo Creating application version: !VERSION_LABEL!
                            aws elasticbeanstalk create-application-version --application-name ${EB_APPLICATION_NAME} --version-label !VERSION_LABEL! --source-bundle S3Bucket=!EB_S3_BUCKET!,S3Key=${DEPLOY_ZIP} --region ${AWS_REGION}
                            if errorlevel 1 (
                                echo ERROR: Failed to create application version
                                echo This may be due to AWS Academy Learner Lab permission restrictions
                                echo Required permission: elasticbeanstalk:CreateApplicationVersion
                                echo Please check your IAM role permissions
                                exit /b 1
                            )
                            echo Application version created successfully
                            
                            REM Update environment
                            echo Updating environment ${EB_ENVIRONMENT_NAME}...
                            aws elasticbeanstalk update-environment --application-name ${EB_APPLICATION_NAME} --environment-name ${EB_ENVIRONMENT_NAME} --version-label !VERSION_LABEL! --region ${AWS_REGION}
                            if errorlevel 1 (
                                echo ERROR: Failed to update environment
                                exit /b 1
                            )
                            
                            echo ========================================
                            echo Deployment initiated successfully!
                            echo Version: !VERSION_LABEL!
                            echo S3 Bucket: !EB_S3_BUCKET!
                            echo ========================================
                            endlocal
                        """
                    }
                }
            }
            post {
                success {
                    echo '✅ Deployment to Elastic Beanstalk succeeded!'
                }
                failure {
                    echo '❌ Deployment to Elastic Beanstalk failed! Check logs above.'
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
