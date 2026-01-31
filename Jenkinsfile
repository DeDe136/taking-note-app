pipeline {
    agent any
    environment {
        // --- Cấu hình chung ---
        AWS_REGION      = "ap-southeast-1" // Định nghĩa Region
        ECR_REGISTRY    = "954692413669.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPOSITORY  = "taking-note-app"
        IMAGE_TAG       = "ver-${BUILD_ID}" // Tag image với build ID
        FULL_IMAGE      = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}" // URL đầy đủ của image

        // --- Cấu hình ECS ---
        TASK_FAMILY     = "taking-note-app-task-def"
        CLUSTER_NAME    = "taking-note-app-ecs-cluster"
        SERVICE_NAME    = "taking-note-app-ecs-service"

        // --- Biến tạm thời (không cần sửa) ---
        TASK_DEFINITION     = ""
        NEW_TASK_DEFINITION = ""
        NEW_TASK_INFO       = ""
        NEW_REVISION        = ""
    }
    stages {
        // stage('Checkout') {
        //     steps {
                
        //         git 'https://github.com/vantai13/taking-note.git' 
        //     }
        // }
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

        stage('Update ECS Service') {
            steps {
                // Sử dụng script block để dễ lấy output từ lệnh sh
                script {
                    // 1. Lấy định nghĩa task definition hiện tại (dạng JSON)
                    TASK_DEFINITION = sh(script: "aws ecs describe-task-definition --task-definition ${TASK_FAMILY} --region ${AWS_REGION}", returnStdout: true).trim()

                    // 2. Tạo định nghĩa task mới bằng cách cập nhật URL image dùng jq
                    //    Loại bỏ các trường không cần thiết/gây lỗi khi đăng ký lại
                    NEW_TASK_DEFINITION = sh(script: """
                        echo '${TASK_DEFINITION}' | jq --arg IMAGE "${FULL_IMAGE}" '
                        .taskDefinition |
                        .containerDefinitions[0].image = \$IMAGE |
                        del(.taskDefinitionArn) |
                        del(.revision) |
                        del(.status) |
                        del(.requiresAttributes) |
                        del(.compatibilities) |
                        del(.registeredAt) |
                        del(.registeredBy)'
                    """, returnStdout: true).trim()

                    // 3. Đăng ký revision mới của task definition
                    NEW_TASK_INFO = sh(script: "aws ecs register-task-definition --region ${AWS_REGION} --cli-input-json '${NEW_TASK_DEFINITION}'", returnStdout: true).trim()

                    // 4. Lấy số revision mới từ output JSON
                    NEW_REVISION = sh(script: "echo '${NEW_TASK_INFO}' | jq -r '.taskDefinition.revision'", returnStdout: true).trim() // -r để lấy chuỗi thuần

                    echo "Successfully registered new task definition revision: ${NEW_REVISION}"

                    // 5. Cập nhật ECS Service để sử dụng revision mới và ép buộc triển khai mới
                    sh """
                        set -e # Dừng ngay nếu có lỗi
                        aws ecs update-service --cluster ${CLUSTER_NAME} \\
                                               --service ${SERVICE_NAME} \\
                                               --task-definition ${TASK_FAMILY}:${NEW_REVISION} \\
                                               --force-new-deployment \\
                                               --region ${AWS_REGION}
                        echo "Successfully triggered update for service ${SERVICE_NAME} in cluster ${CLUSTER_NAME}"
                    """
                }
            }
        }
    }
}