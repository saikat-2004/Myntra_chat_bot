CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    brand TEXT,
    product_name TEXT,
    original_price TEXT,
    discounted_price TEXT,
    rating TEXT,
    product_url TEXT,
    breadcrumbs TEXT,
    category TEXT DEFAULT 'Lipstick',
    scrape_date DATE
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    user_message TEXT,
    bot_response TEXT,
    query_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);