import json
import hmac
import hashlib
import httpx

WEBHOOK_URL = "http://localhost:8000/api/v1/webhook"
SECRET = "supersecretkey123"

def send_mock_push_event(commit_sha: str = "a1b2c3d4e5f67890", repo_name: str = "demo-gitops-repo"):
    payload = {
        "ref": "refs/heads/main",
        "before": "0000000000000000000000000000000000000000",
        "after": commit_sha,
        "repository": {
            "name": repo_name,
            "full_name": f"org/{repo_name}",
            "clone_url": f"https://github.com/org/{repo_name}.git"
        },
        "head_commit": {
            "id": commit_sha,
            "message": "feat: update image tag to nginx:alpine",
            "author": {
                "name": "DevOps Engineer",
                "email": "devops@example.com"
            }
        }
    }

    payload_bytes = json.dumps(payload).encode("utf-8")

    # Generate HMAC-SHA256 signature
    signature = hmac.new(SECRET.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}",
        "User-Agent": "GitHub-Hookshot/mock"
    }

    print(f"[*] Sending mock push event for commit: {commit_sha}")
    print(f"[*] Signature: sha256={signature}")

    response = httpx.post(WEBHOOK_URL, content=payload_bytes, headers=headers)
    print(f"[*] Response Status: {response.status_code}")
    print(f"[*] Response Body: {response.json()}")

if __name__ == "__main__":
    send_mock_push_event()