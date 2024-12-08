source .env

SECRETS_NAME=$PROJECT_NAME-$FOUNDATION_MODEL_NAME-secrets
echo "Creating $SECRETS_NAME secrets..."

SECRET_STRING="{\"OPENAI_API_KEY\":\"$OPENAI_API_KEY\",\"MARKET_API_KEY\":\"$MARKET_API_KEY\"}"

aws secretsmanager create-secret --name $SECRETS_NAME --secret-string "$SECRET_STRING"
