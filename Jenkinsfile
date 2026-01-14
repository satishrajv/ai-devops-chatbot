pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'ai-devops-flask-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Git branch to build')
        choice(name: 'ENVIRONMENT', choices: ['development', 'staging', 'production'], description: 'Deployment environment')
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out branch: ${params.BRANCH}"
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/${params.BRANCH}"]],
                    userRemoteConfigs: [[url: 'https://github.com/satishrajv/AI-DevOps-chatbot.git']]
                ])
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                dir('flask_app') {
                    sh '''
                        python3 -m venv venv || python -m venv venv
                        . venv/bin/activate || venv\\Scripts\\activate
                        pip install -r requirements.txt
                        pip install pytest pytest-cov flake8
                    '''
                }
            }
        }

        stage('Lint') {
            steps {
                echo 'Running linting checks...'
                dir('flask_app') {
                    sh '''
                        . venv/bin/activate || venv\\Scripts\\activate
                        flake8 app.py --max-line-length=120 --ignore=E501 || true
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                dir('flask_app') {
                    sh '''
                        . venv/bin/activate || venv\\Scripts\\activate
                        python -c "from app import app; print('App imports successfully')"
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                dir('flask_app') {
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Push to Registry') {
            when {
                expression { params.ENVIRONMENT == 'staging' || params.ENVIRONMENT == 'production' }
            }
            steps {
                echo 'Pushing image to registry...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} \$DOCKER_USER/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push \$DOCKER_USER/${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to ${params.ENVIRONMENT} environment..."
                script {
                    if (params.ENVIRONMENT == 'development') {
                        sh """
                            docker stop flask-app-dev || true
                            docker rm flask-app-dev || true
                            docker run -d --name flask-app-dev -p 5001:5000 \
                                -e ENVIRONMENT=development \
                                -e BUILD_NUMBER=${BUILD_NUMBER} \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                        """
                    } else if (params.ENVIRONMENT == 'staging') {
                        sh """
                            docker stop flask-app-staging || true
                            docker rm flask-app-staging || true
                            docker run -d --name flask-app-staging -p 5002:5000 \
                                -e ENVIRONMENT=staging \
                                -e BUILD_NUMBER=${BUILD_NUMBER} \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                        """
                    } else if (params.ENVIRONMENT == 'production') {
                        sh """
                            docker stop flask-app-prod || true
                            docker rm flask-app-prod || true
                            docker run -d --name flask-app-prod -p 5000:5000 \
                                -e ENVIRONMENT=production \
                                -e BUILD_NUMBER=${BUILD_NUMBER} \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                        """
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                echo 'Running health check...'
                script {
                    def port = params.ENVIRONMENT == 'development' ? '5001' :
                               params.ENVIRONMENT == 'staging' ? '5002' : '5000'

                    sh """
                        sleep 5
                        curl -f http://localhost:${port}/health || exit 1
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully for ${params.ENVIRONMENT}!"
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}
