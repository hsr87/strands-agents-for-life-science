#!/bin/bash

# AWS Workshop Studio Event Engine Auto-Setup Script
# This script is designed to be run automatically when an event account is created

set -e

echo "🚀 Starting Strands Agents Workshop Infrastructure Deployment"
echo "================================================="

# Configuration
STACK_NAME="strands-workshop-auto"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
TEMPLATE_URL="https://aws-workshop-templates-public.s3.amazonaws.com/strands-agents-life-science/master_stack.yaml"

# Auto-generated secure password
DB_PASSWORD=$(openssl rand -base64 12 | tr -d "/@\"+")

# Check AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS credentials not configured. Please configure AWS CLI."
    exit 1
fi

echo "📍 Deployment Region: $REGION"
echo "📦 Stack Name: $STACK_NAME"

# Enable Bedrock model access
echo ""
echo "🤖 Enabling Bedrock Model Access..."
echo "--------------------------------"

# Function to enable model access
enable_bedrock_model() {
    local model_id=$1
    echo "  Enabling $model_id..."

    aws bedrock put-model-invocation-logging-configuration \
        --logging-config "{}" \
        --region $REGION 2>/dev/null || true

    aws bedrock request-model-access \
        --model-id "$model_id" \
        --region $REGION 2>/dev/null || true
}

# Enable required models
enable_bedrock_model "amazon.titan-embed-text-v1"
enable_bedrock_model "anthropic.claude-3-5-sonnet-20240620-v1:0"
enable_bedrock_model "anthropic.claude-3-sonnet-20240229-v1:0"

echo "✅ Bedrock models enabled"

# Deploy CloudFormation stack
echo ""
echo "☁️ Deploying CloudFormation Stack..."
echo "--------------------------------"

aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-url $TEMPLATE_URL \
    --parameters \
        ParameterKey=DatabaseName,ParameterValue=agentdb \
        ParameterKey=DBUsername,ParameterValue=dbadmin \
        ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD \
        ParameterKey=WorkshopUserEmail,ParameterValue=noreply@workshop.aws \
        ParameterKey=DeploymentNotificationTopic,ParameterValue=strands-notifications \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --region $REGION \
    --on-failure DO_NOTHING

echo "✅ Stack deployment initiated"

# Create parameter store entries for workshop
echo ""
echo "🔐 Storing Workshop Parameters..."
echo "--------------------------------"

aws ssm put-parameter \
    --name "/workshop/strands/db_password" \
    --value "$DB_PASSWORD" \
    --type "SecureString" \
    --overwrite \
    --region $REGION

aws ssm put-parameter \
    --name "/workshop/strands/stack_name" \
    --value "$STACK_NAME" \
    --type "String" \
    --overwrite \
    --region $REGION

echo "✅ Parameters stored securely"

# Setup SageMaker Studio Domain (if not exists)
echo ""
echo "🎨 Checking SageMaker Studio Domain..."
echo "--------------------------------"

DOMAIN_ID=$(aws sagemaker list-domains --region $REGION --query "Domains[0].DomainId" --output text 2>/dev/null || echo "None")

if [ "$DOMAIN_ID" == "None" ] || [ "$DOMAIN_ID" == "null" ]; then
    echo "  Creating new SageMaker Studio Domain..."

    # Get default VPC and subnets
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --region $REGION --query "Vpcs[0].VpcId" --output text)
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --region $REGION --query "Subnets[*].SubnetId" --output text | tr '\t' ',' | cut -d',' -f1,2)

    # Create execution role for SageMaker
    ROLE_NAME="SageMakerStudioRole-Workshop"

    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }' 2>/dev/null || true

    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess 2>/dev/null || true

    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text)

    # Create Studio Domain
    aws sagemaker create-domain \
        --domain-name "strands-workshop-domain" \
        --auth-mode IAM \
        --default-user-settings "{
            \"ExecutionRole\": \"$ROLE_ARN\"
        }" \
        --vpc-id $VPC_ID \
        --subnet-ids $(echo $SUBNET_IDS | tr ',' ' ') \
        --region $REGION

    echo "✅ SageMaker Studio Domain created"
else
    echo "✅ SageMaker Studio Domain exists: $DOMAIN_ID"
fi

# Clone workshop repository to S3 for easy access
echo ""
echo "📚 Preparing Workshop Materials..."
echo "--------------------------------"

BUCKET_NAME="strands-workshop-materials-${AWS_ACCOUNT_ID}"

# Create S3 bucket for workshop materials
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || true

# Download and upload workshop materials
TMP_DIR=$(mktemp -d)
cd $TMP_DIR

git clone https://github.com/aws-samples/strands-agents-for-life-science.git
cd strands-agents-for-life-science

# Upload notebooks to S3
aws s3 sync notebook/ s3://$BUCKET_NAME/notebooks/ --region $REGION

echo "✅ Workshop materials uploaded to S3: $BUCKET_NAME"

# Cleanup
cd /
rm -rf $TMP_DIR

# Print status and next steps
echo ""
echo "========================================"
echo "🎉 Workshop Infrastructure Deployment Initiated!"
echo "========================================"
echo ""
echo "📊 Deployment Status:"
echo "  • Stack Name: $STACK_NAME"
echo "  • Region: $REGION"
echo "  • Status: CREATING (35-45 minutes)"
echo ""
echo "📋 Next Steps:"
echo "  1. Monitor stack progress:"
echo "     https://console.aws.amazon.com/cloudformation/home?region=$REGION"
echo ""
echo "  2. Access SageMaker Studio:"
echo "     https://console.aws.amazon.com/sagemaker/home?region=$REGION#/studio"
echo ""
echo "  3. Workshop materials available at:"
echo "     s3://$BUCKET_NAME/notebooks/"
echo ""
echo "  4. Database credentials stored in:"
echo "     AWS Systems Manager Parameter Store"
echo ""
echo "⏱️ Estimated completion time: 35-45 minutes"
echo ""
echo "💡 You can start Lab 1 immediately while the infrastructure deploys!"
echo ""

# Store deployment info for later reference
cat > /tmp/workshop-info.json <<EOF
{
  "stack_name": "$STACK_NAME",
  "region": "$REGION",
  "bucket": "$BUCKET_NAME",
  "deployment_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "db_username": "dbadmin",
  "db_name": "agentdb"
}
EOF

aws s3 cp /tmp/workshop-info.json s3://$BUCKET_NAME/deployment-info.json --region $REGION

echo "✅ Deployment information saved"
echo ""
echo "🚀 Workshop setup script completed successfully!"