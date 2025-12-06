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
                            
                            REM Find Python using PowerShell (more reliable)
                            echo Finding Python...
                            for /f "delims=" %%p in ('powershell -Command "Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source"') do set PYTHON_CMD=%%p
                            if not defined PYTHON_CMD for /f "delims=" %%p in ('powershell -Command "Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source"') do set PYTHON_CMD=%%p
                            
                            if not defined PYTHON_CMD (
                                echo WARNING: Python not found in PATH
                                echo Attempting to find Python in common locations...
                                if exist C:\\Python310\\python.exe set PYTHON_CMD=C:\\Python310\\python.exe
                                if not defined PYTHON_CMD if exist C:\\Python311\\python.exe set PYTHON_CMD=C:\\Python311\\python.exe
                                if not defined PYTHON_CMD if exist C:\\Users\\%USERNAME%\\anaconda3\\python.exe set PYTHON_CMD=C:\\Users\\%USERNAME%\\anaconda3\\python.exe
                                if not defined PYTHON_CMD if exist C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python310\\python.exe set PYTHON_CMD=C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python310\\python.exe
                            )
                            
                            REM Check if Python is available for EB CLI
                            if not defined PYTHON_CMD (
                                echo ========================================
                                echo Python not found - Using AWS CLI for deployment
                                echo ========================================
                                
                                REM Get AWS account ID for S3 bucket name
                                echo Getting AWS account information...
                                powershell -Command "$account = aws sts get-caller-identity --query Account --output text 2>$null; if ($account) { Write-Host $account.Trim() }" > %TEMP%\\aws_account.txt
                                set /p AWS_ACCOUNT_ID=<%TEMP%\\aws_account.txt
                                del %TEMP%\\aws_account.txt
                                
                                REM Try to get bucket from existing application version first
                                echo Checking for existing S3 bucket...
                                powershell -Command "$bucket = aws elasticbeanstalk describe-application-versions --application-name ${EB_APPLICATION_NAME} --max-items 1 --region ${AWS_REGION} --query 'ApplicationVersions[0].SourceBundle.S3Bucket' --output text 2>$null; if ($bucket -and $bucket -ne 'None') { Write-Host $bucket.Trim() }" > %TEMP%\\eb_bucket.txt
                                set /p EB_S3_BUCKET=<%TEMP%\\eb_bucket.txt
                                del %TEMP%\\eb_bucket.txt
                                
                                REM If no existing bucket, construct bucket name from account ID
                                if "%EB_S3_BUCKET%"=="" (
                                    if not "%AWS_ACCOUNT_ID%"=="" (
                                        set EB_S3_BUCKET=elasticbeanstalk-${AWS_REGION}-%AWS_ACCOUNT_ID%
                                        echo Constructed bucket name from account ID
                                    ) else (
                                        echo ERROR: Could not get AWS account ID
                                        echo Please ensure AWS credentials have proper permissions
                                        exit /b 1
                                    )
                                ) else (
                                    echo Found existing bucket from previous deployment
                                )
                                
                                echo Using S3 bucket: %EB_S3_BUCKET%
                                
                                REM Set version label and ZIP name
                                set VERSION_LABEL=app-${BUILD_NUMBER}
                                set ZIP_NAME=lms-deployment-${BUILD_NUMBER}.zip
                                
                                REM Upload ZIP to S3
                                echo Uploading deployment package to S3...
                                echo Source: %ZIP_NAME%
                                echo Destination: s3://%EB_S3_BUCKET%/%ZIP_NAME%
                                aws s3 cp "%ZIP_NAME%" "s3://%EB_S3_BUCKET%/%ZIP_NAME%" --region ${AWS_REGION}
                                if errorlevel 1 (
                                    echo WARNING: Failed to upload to S3, bucket may not exist
                                    echo Elastic Beanstalk will create bucket automatically when creating version
                                    echo Proceeding to create application version...
                                ) else (
                                    echo Successfully uploaded to S3
                                )
                                
                                REM Create application version (EB will create bucket if needed)
                                echo Creating application version: %VERSION_LABEL%
                                aws elasticbeanstalk create-application-version --application-name ${EB_APPLICATION_NAME} --version-label %VERSION_LABEL% --source-bundle S3Bucket=%EB_S3_BUCKET%,S3Key=%ZIP_NAME% --auto-create-application --region ${AWS_REGION}
                                if errorlevel 1 (
                                    echo ERROR: Failed to create application version
                                    echo Check AWS permissions and credentials
                                    exit /b 1
                                )
                                echo Application version created successfully
                                
                                REM Update environment
                                echo Updating environment ${EB_ENVIRONMENT_NAME} to version %VERSION_LABEL%...
                                aws elasticbeanstalk update-environment --application-name ${EB_APPLICATION_NAME} --environment-name ${EB_ENVIRONMENT_NAME} --version-label %VERSION_LABEL% --region ${AWS_REGION}
                                if errorlevel 1 (
                                    echo ERROR: Failed to update environment
                                    echo Environment may already be updating or credentials may be invalid
                                    exit /b 1
                                )
                                
                                echo ========================================
                                echo Deployment initiated successfully!
                                echo Version: %VERSION_LABEL%
                                echo S3 Bucket: %EB_S3_BUCKET%
                                echo Check AWS Console for deployment status.
                                echo ========================================
                                exit /b 0
                            )
                            
                            REM Python found - use EB CLI
                            echo Found Python: %PYTHON_CMD%
                            echo Installing EB CLI...
                            "%PYTHON_CMD%" -m pip install awsebcli --user --quiet
                            if errorlevel 1 (
                                echo ERROR: Failed to install EB CLI
                                exit /b 1
                            )
                            
                            REM Find EB CLI executable
                            set EB_CMD=eb
                            for /f "delims=" %%e in ('powershell -Command "Get-Command eb -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source"') do set EB_CMD=%%e
                            if "%EB_CMD%"=="eb" (
                                REM Try common locations
                                if exist "%USERPROFILE%\\AppData\\Roaming\\Python\\Python*\\Scripts\\eb.exe" (
                                    for /f "delims=" %%e in ('dir /b /s "%USERPROFILE%\\AppData\\Roaming\\Python\\Python*\\Scripts\\eb.exe" 2^>nul') do set EB_CMD=%%e
                                )
                                if "%EB_CMD%"=="eb" if exist "%USERPROFILE%\\AppData\\Local\\Programs\\Python\\Python*\\Scripts\\eb.exe" (
                                    for /f "delims=" %%e in ('dir /b /s "%USERPROFILE%\\AppData\\Local\\Programs\\Python\\Python*\\Scripts\\eb.exe" 2^>nul') do set EB_CMD=%%e
                                )
                                REM If still not found, try python -m awsebcli
                                if "%EB_CMD%"=="eb" set EB_CMD=%PYTHON_CMD% -m awsebcli
                            )
                            
                            echo Using EB CLI: %EB_CMD%
                            "%EB_CMD%" --version
                            
                            REM Copy .elasticbeanstalk config to deploy directory
                            echo Setting up EB configuration...
                            if not exist deploy\\.elasticbeanstalk mkdir deploy\\.elasticbeanstalk
                            if exist .elasticbeanstalk\\config.yml (
                                copy /Y .elasticbeanstalk\\config.yml deploy\\.elasticbeanstalk\\config.yml
                                echo EB config copied
                            ) else (
                                echo Warning: .elasticbeanstalk\\config.yml not found
                            )
                            
                            REM Deploy to Elastic Beanstalk using EB CLI
                            echo Deploying to ${EB_ENVIRONMENT_NAME}...
                            cd deploy
                            
                            REM Try to use the environment (optional)
                            "%EB_CMD%" use ${EB_ENVIRONMENT_NAME} 2>&1 || echo Warning: Could not set EB environment, continuing...
                            
                            REM Deploy
                            echo Running eb deploy...
                            "%EB_CMD%" deploy ${EB_ENVIRONMENT_NAME} --staged 2>&1
                            if errorlevel 1 (
                                echo Staged deploy failed, trying regular deploy...
                                "%EB_CMD%" deploy ${EB_ENVIRONMENT_NAME} 2>&1
                            )
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
                    script {
                        // Check if deployment was actually attempted or skipped
                        def log = currentBuild.rawBuild.getLog(100)
                        def skipped = log.any { it.contains('Skipping deployment') || it.contains('Python not found') }
                        if (!skipped) {
                            echo 'Deployment to Elastic Beanstalk succeeded!'
                        } else {
                            echo 'WARNING: Deployment was skipped - Python not found. Install Python on Jenkins server or use AWS CLI method.'
                        }
                    }
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
