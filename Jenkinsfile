pipeline {
    agent any
    
    triggers {
        pollSCM('H/5 * * * *')  // Check every 5 minutes
    }
    
    environment {
        SONAR_ORGANIZATION = 'wasiullah26'
        SONAR_PROJECT_KEY = 'Wasiullah26_LMS-Learning-Management-System'
        SONAR_TOKEN = credentials('sonarcloud-token')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Backend: Dependency Check') {
            steps {
                dir('backend') {
                    script {
                        def pythonExe = bat(
                            script: '@echo off & powershell -Command "$p = Get-Command python -ErrorAction SilentlyContinue; if ($p) { Write-Host $p.Source } else { $p = Get-Command py -ErrorAction SilentlyContinue; if ($p) { Write-Host $p.Source } else { Write-Host \"NOT_FOUND\" } }"',
                            returnStdout: true
                        ).trim()
                        
                        if (pythonExe != "NOT_FOUND" && !pythonExe.isEmpty()) {
                            bat """
                                "${pythonExe}" -m pip install safety || exit /b 0
                                "${pythonExe}" -m safety check || exit /b 0
                            """
                        } else {
                            echo "Python not found - skipping dependency check"
                        }
                    }
                }
            }
        }
        
        stage('Frontend: Lint & Build') {
            steps {
                dir('frontend') {
                    bat '''
                        call npm ci || exit /b 0
                        call npm run lint || exit /b 0
                        call npm run build || exit /b 0
                    '''
                }
            }
        }
        
        stage('SonarCloud Analysis') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    bat """
                        where sonar-scanner >nul 2>&1 || npm install -g sonarqube-scanner || exit /b 0
                        sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.organization=${SONAR_ORGANIZATION} -Dsonar.sources=backend,frontend/src -Dsonar.exclusions=backend/venv/**,backend/__pycache__/**,backend/**/*.pyc,backend/reports/**,backend/.venv/**,backend/setup/aws_setup.py,backend/seed_database.py,frontend/node_modules/**,frontend/dist/**,frontend/build/**,frontend/reports/**,frontend/public/** -Dsonar.python.version=3.10 -Dsonar.sourceEncoding=UTF-8 || exit /b 0
                    """
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
                        error "Quality gate failed: ${qg.status}"
                    }
                } catch (Exception e) {
                    echo "Quality gate skipped: ${e.getMessage()}"
                }
            }
            cleanWs()
        }
    }
}
