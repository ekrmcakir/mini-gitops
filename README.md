# 🚀 Mini-GitOps Controller

A lightweight, declarative GitOps continuous delivery engine built with Python and FastAPI. It continuously reconciles container runtime state against Git-defined manifests with built-in HMAC authentication, state diffing, readiness probing, atomic swapping, and automated rollbacks.

---

## ✨ Features

- 📜 **Declarative GitOps Workflow**: Uses Git and YAML manifests as the single source of truth for containerized workloads.
- 🔐 **Cryptographic Security**: Validates incoming GitHub webhook payloads using HMAC-SHA256 signatures (`X-Hub-Signature-256`).
- 🔍 **Drift Detection Engine**: Computes granular diffs between Desired State (manifest) and Actual State (Docker container).
- ⚡ **Idempotency**: Skips deployments and avoids container restarts when the system is already in sync.
- 🩺 **Pre-flight Health Checks**: Verifies newly deployed workloads using customizable HTTP readiness probes.
- 🔄 **Atomic Swap & Auto-Rollback**: Temporarily backs up the active container and automatically rolls back if health verification fails.

---

## 🏗️ Architecture Overview

```text
[Developer] ──(git push)──► [GitHub / Webhook Trigger]
                                  │
                        (HMAC-SHA256 Signed POST)
                                  ▼
                     [FastAPI Webhook Receiver]
                                  │
                     (Parse Declarative Manifest)
                                  ▼
                         [Git Sync Engine]
                                  │
                                  ▼
                         [Diff Engine (Drift?)]
                        /                      \
                 [No Drift]                 [Drift Detected]
                      │                            │
                 (Log & Skip)               [Docker Driver]
                                                   │
                                          (Atomic Deploy & Probe)
                                            ├── [Pass] ──► Finalize Deployment
                                            └── [Fail] ──► Trigger Auto-Rollback
```

---

## 📁 Project Structure

```text
mini-gitops/
├── app/
│   ├── __init__.py
│   ├── config.py          # Environment settings and configuration
│   ├── diff_engine.py     # Drift detection logic
│   ├── main.py            # FastAPI entry point & webhook endpoint
│   ├── models.py          # Pydantic schemas for state representation
│   ├── reconciler.py      # Core reconciliation loop & rollback handler
│   ├── runtime_driver.py  # Docker Engine SDK wrapper & healthcheck probes
│   ├── security.py        # HMAC-SHA256 signature verification
│   └── sync_engine.py     # Git clone & YAML manifest parser
├── manifests/
│   └── sample-app.yaml    # Declarative workload specification
├── scripts/
│   ├── mock_webhook.py    # Python webhook simulator with HMAC generation
│   └── send_webhook.sh    # Bash/cURL webhook script
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 🛠️ Getting Started

### 1. Prerequisites

- Python 3.10+
- Docker Desktop or OrbStack running locally

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/ekrmcakir/mini-gitops.git
cd mini-gitops

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Server

Start the reconciliation server with Uvicorn:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing & Usage

Open a second terminal window, activate the virtual environment, and run the mock webhook script:

```bash
source .venv/bin/activate
python scripts/mock_webhook.py
```

### 🔎 Verification Commands

Check running container status:

```bash
docker ps --filter "name=demo-web-service"
```

Verify service connectivity:

```bash
curl http://localhost:8085/
```

---

## 🛡️ Testing Automated Rollback

1. Update `manifests/sample-app.yaml` with an invalid health check path:

```yaml
healthcheck_path: "/this-endpoint-does-not-exist"
```

2. Trigger the webhook:

```bash
python scripts/mock_webhook.py
```

3. **Watch the logs:** The candidate container will fail readiness checks, and the controller will automatically restore the previous healthy container.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
