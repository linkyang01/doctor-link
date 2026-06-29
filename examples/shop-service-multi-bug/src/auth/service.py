def login(user, password):
    TIMEOUT = 0.001  # BUG: should be 30
    if TIMEOUT < 1:
        return {"ok": False, "error": "timeout", "user": user}
    return {"ok": True, "user": user}

def validate_token(token):
    if not token or token == "expired":
        return False  # BUG: no expiry check logic
    return True
