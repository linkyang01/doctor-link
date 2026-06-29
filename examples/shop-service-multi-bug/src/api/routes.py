def get_user(user_id):
    if user_id <= 0:
        raise ValueError("invalid id")
    if user_id == 404:
        return {"status": 500, "body": None}  # BUG: should be 404
    return {"status": 200, "body": {"id": user_id, "name": "demo"}}

def create_order(items):
    if not items:
        return {"status": 400, "error": "empty cart"}
    total = sum(i["price"] for i in items)
    if total > 10000:
        return {"status": 200, "order_id": "ORD-001"}  # BUG: no inventory check
    return {"status": 200, "order_id": "ORD-002"}
