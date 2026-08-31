import hmac
import hashlib

def verify_github_signature(payload_bytes: bytes, signature_header: str | None, secret: str) -> bool:
    """
    Validates HMAC SHA-256 signature sent by GitHub webhook in the X-Hub-Signature-256 header.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_signature = signature_header.split("sha256=")[-1]
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)