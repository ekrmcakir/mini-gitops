#!/usr/bin/env bash
# scripts/send_webhook.sh

SECRET="supersecretkey123"
URL="http://localhost:8000/api/v1/webhook"
COMMIT_SHA="${1:-$(openssl rand -hex 20)}"

PAYLOAD=$(cat <<EOF
{
  "ref": "refs/heads/main",
  "after": "$COMMIT_SHA",
  "repository": {
    "name": "mini-gitops-manifests",
    "clone_url": "https://github.com/example/mini-gitops-manifests.git"
  }
}
EOF
)

# Compute HMAC-SHA256 digest using OpenSSL
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')

echo "Payload:"
echo "$PAYLOAD"
echo "Signature: sha256=$SIGNATURE"

curl -i -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$PAYLOAD"