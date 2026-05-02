def classify_query(user_query: str):
    q = user_query.lower()
    sensitive = ["offer", "discount", "sale", "return", "refund", "exchange", "cancel", "delivery", "price issue", "complaint"]
    if any(word in q for word in sensitive):
        return "redirect"
    if any(word in q for word in ["lipstick", "product", "brand", "price", "buy", "review", "best"]):
        return "product_info"
    return "general"