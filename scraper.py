import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import os

# ── Myntra's actual CSS class names (as of 2025) ──────────────────────────────
SELECTORS = {
    "card":           "li.product-base",
    "brand":          "h3.product-brand",
    "name":           "h4.product-product",
    "orig_price":     "span.product-strike",          # crossed-out original price
    "disc_price":     "span.product-discountedPrice", # actual selling price
    "rating":         "div.product-ratingsCount",
    "link":           "a",                            # first <a> in card
}

def _make_driver():
    options = Options()
    options.add_argument("--headless=new")        # new headless mode (Chrome 112+)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    # Suppress DevTools / GPU noise
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _scroll_and_wait(driver, pause=1.5, scrolls=5):
    """Scroll down incrementally so lazy-loaded product cards render."""
    for _ in range(scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(pause)


def _parse_cards(soup):
    products = []
    cards = soup.select(SELECTORS["card"])
    print(f"   Found {len(cards)} product cards in HTML")

    for card in cards:
        try:
            brand_el   = card.select_one(SELECTORS["brand"])
            name_el    = card.select_one(SELECTORS["name"])
            orig_el    = card.select_one(SELECTORS["orig_price"])
            disc_el    = card.select_one(SELECTORS["disc_price"])
            rating_el  = card.select_one(SELECTORS["rating"])
            link_el    = card.select_one(SELECTORS["link"])

            brand      = brand_el.text.strip()  if brand_el  else "N/A"
            name       = name_el.text.strip()   if name_el   else "N/A"
            orig_price = orig_el.text.strip()   if orig_el   else "N/A"
            disc_price = disc_el.text.strip()   if disc_el   else orig_price
            rating     = rating_el.text.strip() if rating_el else "N/A"
            url        = ("https://www.myntra.com" + link_el["href"]
                          if link_el and link_el.get("href") else "#")

            # Skip placeholder / empty cards
            if brand == "N/A" and name == "N/A":
                continue

            products.append({
                "brand":            brand,
                "product_name":     name,
                "original_price":   orig_price,
                "discounted_price": disc_price,
                "rating":           rating,
                "product_url":      url,
                "breadcrumbs":      "Home / Personal Care / Lipstick",
                "category":         "Lipstick",
            })
        except Exception as e:
            print(f"   Skipping a card due to error: {e}")
            continue

    return products


def scrape_myntra_lipsticks(max_pages=3):
    base_url = "https://www.myntra.com/lipstick"
    driver = _make_driver()
    all_products = []

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}?p={page}" if page > 1 else base_url
            print(f"Scraping page {page}: {url}")
            driver.get(url)

            # Wait until at least one product card is present in the DOM
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["card"]))
                )
            except Exception:
                print(f"   ⚠️  No product cards detected on page {page} — skipping")
                continue

            # Scroll so lazy-loaded cards render
            _scroll_and_wait(driver, pause=1.2, scrolls=6)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            page_products = _parse_cards(soup)
            print(f"   ✅ Parsed {len(page_products)} products from page {page}")
            all_products.extend(page_products)

            time.sleep(2)   # polite delay between pages

    finally:
        driver.quit()

    if not all_products:
        print("❌ No products scraped. Myntra may have changed their HTML structure.")
        print("   → Open https://www.myntra.com/lipstick in Chrome, inspect a product")
        print("     card element, and update the SELECTORS dict at the top of this file.")
        return

    df = pd.DataFrame(all_products).drop_duplicates(subset=["product_url"])
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/products.csv", index=False)
    print(f"\n✅ Scraped {len(df)} products → data/products.csv")

    # ── Load into PostgreSQL (optional — skipped if DB not configured) ─────────
    try:
        from app.models import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        inserted = 0
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO products
                    (brand, product_name, original_price, discounted_price,
                     rating, product_url, breadcrumbs, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                row["brand"], row["product_name"], row["original_price"],
                row["discounted_price"], row["rating"], row["product_url"],
                row["breadcrumbs"], row["category"],
            ))
            inserted += cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ {inserted} new rows inserted into PostgreSQL")
    except Exception as e:
        print(f"⚠️  DB insert skipped: {e}")


if __name__ == "__main__":
    scrape_myntra_lipsticks(max_pages=3)