import psycopg2
from psycopg2.extras import DictCursor
from app.config import Config

def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)

def log_conversation(session_id, user_msg, bot_resp, query_type="general"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO conversations (session_id, user_message, bot_response, query_type)
        VALUES (%s, %s, %s, %s)
    """, (session_id, user_msg, bot_resp, query_type))
    conn.commit()
    cur.close()
    conn.close()

def search_products(query):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("""
        SELECT brand, product_name, discounted_price, rating, product_url 
        FROM products 
        WHERE LOWER(product_name) LIKE %s OR LOWER(brand) LIKE %s
        LIMIT 5
    """, (f"%{query.lower()}%", f"%{query.lower()}%"))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results