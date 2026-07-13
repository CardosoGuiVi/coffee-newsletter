#!/bin/bash
source .env

cat > /tmp/sam_params.yaml << EOF
DatabasePassword: "${COFFEE_DATABASE__PASSWORD}"
AnthropicApiKey: "${COFFEE_AI_PROVIDER__API_KEY}"
ResendApiKey: "${COFFEE_RESEND_API_KEY}"
SecretKey: "${COFFEE_SECRET_KEY}"
EOF