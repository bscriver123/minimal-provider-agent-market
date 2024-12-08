#!/bin/bash

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
CPU_ARCHITECTURE=$(uname -m | tr '[:upper:]' '[:lower:]')
AWS_REGION=$(aws configure get region)

source .env

cd infrastructure
terraform init

TERRAFORM_WORKSPACE_NAME=$(echo "$PROJECT_NAME-$FOUNDATION_MODEL_NAME-$CPU_ARCHITECTURE" | tr '/' '-')

if terraform workspace list | grep -q -w "$TERRAFORM_WORKSPACE_NAME"; then
  echo "Workspace $TERRAFORM_WORKSPACE_NAME exists. Selecting it..."
else
  echo "Workspace $TERRAFORM_WORKSPACE_NAME does not exist. Creating and selecting it..."
  terraform workspace new "$TERRAFORM_WORKSPACE_NAME"
fi

terraform workspace select "$TERRAFORM_WORKSPACE_NAME"

terraform plan \
  --var "aws_region=$AWS_REGION" \
  --var "project_name=$PROJECT_NAME" \
  --var "foundation_model_name=$FOUNDATION_MODEL_NAME" \
  --var "cpu_architecture=$CPU_ARCHITECTURE" \
  --var "openai_api_key=$OPENAI_API_KEY" \
  --var "market_api_key=$MARKET_API_KEY" \
  --var "github_pat=$GITHUB_PAT" \
  --var "max_bid=$MAX_BID"

terraform apply \
  -auto-approve \
  --var "aws_region=$AWS_REGION" \
  --var "project_name=$PROJECT_NAME" \
  --var "foundation_model_name=$FOUNDATION_MODEL_NAME" \
  --var "cpu_architecture=$CPU_ARCHITECTURE" \
  --var "openai_api_key=$OPENAI_API_KEY" \
  --var "market_api_key=$MARKET_API_KEY" \
  --var "github_pat=$GITHUB_PAT" \
  --var "max_bid=$MAX_BID"

# Get the instance ID
INSTANCE_ID=$(terraform output -raw instance_id)

echo "Waiting for instance to be ready..."
sleep 60  # Wait for instance to fully boot

# Define the commands as separate steps with better error handling
COMMANDS=(
    "timeout 120 sudo apt-get update && timeout 120 sudo apt-get install -y python3-pip git docker.io"
    "sudo systemctl enable docker && sudo systemctl start docker && sudo usermod -aG docker ubuntu && newgrp docker && docker pull paulgauthier/aider"
    "cd /home/ubuntu && rm -rf ${PROJECT_NAME} && git clone https://oauth2:${GITHUB_PAT}@github.com/GroupLang/${PROJECT_NAME}.git"
    "cd /home/ubuntu/${PROJECT_NAME} && { sudo mkdir -p /home/ubuntu/${PROJECT_NAME} && printf 'PROJECT_NAME=%s\\nFOUNDATION_MODEL_NAME=%s\\nOPENAI_API_KEY=%s\\nMARKET_API_KEY=%s\\nGITHUB_PAT=%s\\nMAX_BID=%s\\nGITHUB_USERNAME=%s\\nGITHUB_EMAIL=%s\\n' '${PROJECT_NAME}' '${FOUNDATION_MODEL_NAME}' '${OPENAI_API_KEY}' '${MARKET_API_KEY}' '${GITHUB_PAT}' '${MAX_BID}' '${GITHUB_USERNAME}' '${GITHUB_EMAIL}' | sudo tee /home/ubuntu/${PROJECT_NAME}/.env && echo '.env file created successfully' && sudo cat /home/ubuntu/${PROJECT_NAME}/.env; }"
    "cd /home/ubuntu/${PROJECT_NAME} && timeout 60 sudo pip3 install --no-cache-dir -r requirements.txt > pip_install.log 2>&1"
    # "cd /home/ubuntu/${PROJECT_NAME} && nohup python3 main.py"
)

# sudo chown -R $(id -u):$(id -g) /home/ubuntu/minimal-provider-agent-market  # change ownership back to the user
# docker run -it --user $(id -u):$(id -g) --volume /home/ubuntu/${PROJECT_NAME}:/app paulgauthier/aider --openai-api-key $OPENAI_API_KEY --env-file .env


# Modify the run_command function to use simpler JSON formatting
run_command() {
    local command=$1
    local step=$2
    echo "----------------------------------------"
    echo "Starting step $step..."
    echo "Command to execute: $command"
    
    # Create a temporary JSON file for the command
    local temp_json=$(mktemp)
    echo "{\"commands\":[\"$command\"]}" > "$temp_json"
    
    # Send command with increased timeout
    COMMAND_OUTPUT=$(aws ssm send-command \
        --instance-ids "$INSTANCE_ID" \
        --document-name "AWS-RunShellScript" \
        --parameters "file://$temp_json" \
        --region "$AWS_REGION" \
        --timeout-seconds 600 \
        --output json)
    
    # Remove temporary file
    rm "$temp_json"

    COMMAND_ID=$(echo "$COMMAND_OUTPUT" | grep -o '"CommandId": "[^"]*' | cut -d'"' -f4)

    if [ -z "$COMMAND_ID" ]; then
        echo "Failed to get Command ID for step $step"
        exit 1
    fi

    echo "Command ID: $COMMAND_ID"
    
    # Wait for completion
    while true; do
        STATUS=$(aws ssm list-commands \
            --command-id "$COMMAND_ID" \
            --output json | grep -o '"Status": "[^"]*' | cut -d'"' -f4)
        
        echo "Step $step status: $STATUS"
        
        if [ "$STATUS" = "Success" ]; then
            echo "Step $step completed successfully!"
            # Get and display command output
            aws ssm get-command-invocation \
                --command-id "$COMMAND_ID" \
                --instance-id "$INSTANCE_ID" \
                --plugin-name "aws:RunShellScript" \
                --query "StandardOutputContent" \
                --output text
            break
        elif [ "$STATUS" = "Failed" ] || [ "$STATUS" = "Cancelled" ] || [ "$STATUS" = "TimedOut" ]; then
            echo "Step $step failed with status: $STATUS"
            echo "Error output:"
            aws ssm get-command-invocation \
                --command-id "$COMMAND_ID" \
                --instance-id "$INSTANCE_ID" \
                --plugin-name "aws:RunShellScript" \
                --query "StandardErrorContent" \
                --output text
            exit 1
        fi
        
        sleep 10
    done
}

# Execute each command step by step
for i in "${!COMMANDS[@]}"; do
    run_command "${COMMANDS[$i]}" "$((i+1))"
done

echo "All setup commands completed successfully!"
