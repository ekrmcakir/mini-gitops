from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks, status
import logging
from app.config import settings
from app.security import verify_github_signature
from app.reconciler import Reconciler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api")

app = FastAPI(
    title="Mini-GitOps Controller",
    description="Lightweight GitOps and continuous reconciliation engine for container workloads.",
    version="0.1.0"
)

reconciler = Reconciler()

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/webhook", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None)
):
    payload_bytes = await request.body()

    if not verify_github_signature(payload_bytes, x_hub_signature_256, settings.WEBHOOK_SECRET):
        logger.warning("Unauthorized webhook request rejected: Invalid HMAC signature.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid HMAC Signature")

    payload = await request.json()
    commit_sha = payload.get("after")
    logger.info(f"Accepted valid webhook event. Commit: {commit_sha}")

    # Process reconciliation in the background to avoid webhook timeout
    background_tasks.add_task(reconciler.reconcile, commit_sha)

    return {"status": "queued", "commit": commit_sha}