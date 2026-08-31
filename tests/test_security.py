from app.security import verify_github_signature
import hmac
import hashlib

def test_verify_github_signature_valid():
    secret = "testsecret123"
    payload = b'{"test": "data"}'
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    header = f"sha256={signature}"

    assert verify_github_signature(payload, header, secret) is True

def test_verify_github_signature_invalid():
    secret = "testsecret123"
    payload = b'{"test": "data"}'
    invalid_header = "sha256=invalidhexsignature123"

    assert verify_github_signature(payload, invalid_header, secret) is False
