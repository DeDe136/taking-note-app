pipeline {
    agent any
    environment {
        // --- Cấu hình chung ---
        AWS_REGION      = "ap-southeast-1" // Định nghĩa Region
        ECR_REGISTRY    = "864304568243.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPOSITORY  = "taking-note-app"
        IMAGE_TAG       = "ver-${BUILD_ID}" // Tag image với build ID
        FULL_IMAGE      = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}" // URL đầy đủ của image

        // --- Cấu hình ECS ---
        TASK_FAMILY     = "taking-note-app-fargate"
        CLUSTER_NAME    = "ecs-cluster"
        SERVICE_NAME    = "taking-note-app-service"
    }
    stages {
        stage('Checkout') {
            steps {
                
                git branch: 'main', url: 'https://github.com/DeDe136/taking-note-app.git'
            }
        }
        stage('Build') {
            steps {
                // Build image với tag local trước
                sh "docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} ."
            }
        }

        stage('Upload image to ECR') {
            steps {
                // Login vào ECR
                sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                // Tag image với đường dẫn ECR đầy đủ
                sh "docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${FULL_IMAGE}"
                // Push image lên ECR
                sh "docker push ${FULL_IMAGE}"
            }
        }

        stage('Update ECS via STDIN') {
            steps {
                script {
                    // 1. Lấy task definition hiện tại từ ECS (dạng JSON)
                    def currentTaskDef = sh(
                        script: """
                        aws ecs describe-task-definition \
                          --task-definition ${TASK_FAMILY} \
                          --region ${AWS_REGION}
                        """,
                        returnStdout: true
                    ).trim()

                    // 2. Dùng jq để:
                    //  - Lấy phần taskDefinition
                    //  - Thay image container thành image mới
                    //  - Xóa các field AWS không cho đăng ký lại
                    def newTaskDef = sh(
                        script: """
                        echo '${currentTaskDef}' | jq --arg IMAGE "${FULL_IMAGE}" '
                          .taskDefinition
                          | .containerDefinitions[0].image = \$IMAGE
                          | del(
                              .taskDefinitionArn,
                              .revision,
                              .status,
                              .requiresAttributes,
                              .compatibilities,
                              .registeredAt,
                              .registeredBy
                          )
                        '
                        """,
                        returnStdout: true
                    ).trim()

                    // 3. Đăng ký task definition mới
                    def registerOutput = sh(
                        script: """
                        aws ecs register-task-definition \
                          --region ${AWS_REGION} \
                          --cli-input-json '${newTaskDef}'
                        """,
                        returnStdout: true
                    ).trim()
                
                    // 4. Lấy số revision trực tiếp từ output JSON
                    env.NEW_REVISION = sh(
                        script: """
                        echo '${registerOutput}' | jq -r '.taskDefinition.revision'
                        """,
                        returnStdout: true
                    ).trim()
                
                    echo "New task definition revision: ${env.NEW_REVISION}"
                }
            }
        }

        stage('Update ECS Service') {
            steps {
                sh """
                    # 1. Cập nhật ECS Service
                    # 2. Service sẽ dùng revision mới nhất của task definition
                    # 3. --force-new-deployment:
                    #    - ECS stop task cũ
                    #    - pull image mới
                    #    - chạy task mới
                    aws ecs update-service \
                        --cluster ${CLUSTER_NAME} \
                        --service ${SERVICE_NAME} \
                        --task-definition ${TASK_FAMILY}:${NEW_REVISION} \
                        --force-new-deployment \
                        --region ${AWS_REGION}
                """
            }
        }
    }
}