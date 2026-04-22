
# Name    : Chandana Jagadish
# Task    : Task 1 - Amazon.in Web Scraper
# Date    : April 2026


# What libraries I am using and why:
# requests      - to open/fetch the Amazon webpage like a browser
# BeautifulSoup - to read through the HTML and find specific data
# pandas        - to organise data into a table and save as CSV
# datetime      - to get current date+time for the output filename
# time, random  - to add delays between requests (avoid being blocked)
# re            - regular expressions, used to search text patterns
# urllib.parse  - to clean up messy sponsored product URLs

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
import re
from urllib.parse import urlparse, parse_qs, unquote


# Browser headers - Amazon blocks plain scripts so we pretend like Chrome
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}



# Purpose: Sponsored/Ad product links on Amazon are messy.
def clean_amazon_url(href):
    if not href or href == "N/A":
        return "N/A"

    if "/sspa/click" in href:
        try:
            parsed = urlparse("https://www.amazon.in" + href)
            params = parse_qs(parsed.query)
            if "url" in params:
                real_path = unquote(params["url"][0])
                if "/dp/" in real_path:
                    parts = real_path.split("/dp/")
                    asin = parts[1].split("/")[0].split("?")[0]
                    return "https://www.amazon.in" + parts[0] + "/dp/" + asin + "/"
        except Exception:
            pass

    if href.startswith("/"):
        return "https://www.amazon.in" + href.split("/ref=")[0]

    return href

# Purpose: Get the product title from a product card.
def extract_title(card):

    # Approach 1: h2 > span 
    h2 = card.find("h2")
    if h2:
        span = h2.find("span")
        if span:
            text = span.get_text(strip=True)
            if text:
                return text

    # Approach 2: span with class a-text-normal
    span = card.find("span", class_="a-text-normal")
    if span:
        text = span.get_text(strip=True)
        if text:
            return text

    # Approach 3: anchor tag with a title attribute
    a_tag = card.find("a", attrs={"title": True})
    if a_tag:
        return a_tag["title"].strip()

    return "N/A"


# FUNCTION 3 - extract_rating
# Purpose: Get the star rating of a product.
def extract_rating(card):

    # Method 1: <span class="a-icon-alt"> 
    icon_alt = card.find("span", class_="a-icon-alt")
    if icon_alt:
        text = icon_alt.get_text(strip=True)
        if "out of 5" in text:
            return text.split(" out of")[0].strip()

    # Method 2: <i> star icon tag - inner span
    star_i = card.find("i", class_=re.compile(r"a-icon-star"))
    if star_i:
        span = star_i.find("span", class_="a-icon-alt")
        if span:
            text = span.get_text(strip=True)
            if "out of 5" in text:
                return text.split(" out of")[0].strip()

    # Method 3: <a> tag with aria-label containing rating
    for a_tag in card.find_all("a", {"aria-label": True}):
        label = a_tag.get("aria-label", "")
        if "out of 5 stars" in label:
            return label.split(" out of")[0].strip()

    # Method 4: <span> tag with aria-label containing rating
    for span in card.find_all("span", {"aria-label": True}):
        label = span.get("aria-label", "")
        if "out of 5 stars" in label:
            return label.split(" out of")[0].strip()

    # Method 5: Regex scan of entire card HTML as last resort
    card_html = str(card)
    matches = re.findall(r'(\d\.\d)\s+out of\s+5', card_html)
    if matches:
        return matches[0]
    
    return "N/A"

# Purpose: Scrapes all laptop products from one search results page
# This returns a list of dictionaries, one dictionary per product
def scrape_page(page_num, session):
    url = f"https://www.amazon.in/s?k=laptops&page={page_num}"
    print(f"\nFetching page {page_num}")
    print(url)

    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print("ERROR loading page {page_num}: {e}")
        return []
    soup = BeautifulSoup(response.content, "html.parser")

    # Every product card has this attribute: data-component-type="s-search-result"
    cards = soup.find_all("div", {"data-component-type": "s-search-result"})
    print("Found {len(cards)} products on this page.")

    products = []

    for card in cards:
        # To extract each field
        title = extract_title(card)
        rating = extract_rating(card)
        price_tag = card.find("span", class_="a-price-whole")
        price = ("₹" + price_tag.get_text(strip=True).replace(",", "")) if price_tag else "N/A"
        img_tag = card.find("img", class_="s-image")
        image_url= img_tag["src"] if img_tag else "N/A"

        # To check if the word "Sponsored" appears anywhere in the card
        sponsored = card.find(
            lambda tag: tag.name in ["span", "a"]
            and tag.get_text(strip=True) == "Sponsored"
        )
        result_type  = "Ad" if sponsored else "Organic"
        link_tag = card.find("a", class_="a-link-normal", href=True)
        raw_href = link_tag["href"] if link_tag else "N/A"
        product_link = clean_amazon_url(raw_href)

        # This code stores all fields in a dictionary
        products.append({
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Result Type" : result_type,
            "Image URL": image_url,
            "Product Link": product_link,
        })

    return products



# MAIN - This is the main function where the script gets executed
def main():

    print("Amazon.in Laptop Scraper")
    session = requests.Session()
    print("\n Visiting Amazon homepage to get session cookies...")
    try:
        session.get("https://www.amazon.in", headers=HEADERS, timeout=15)
        print("  Done.")
    except Exception:
        print("(Could not reach homepage)")

    time.sleep(random.uniform(2, 3))

    # Scrape multiple pages
    all_products = []
    TOTAL_PAGES = 3

    for page in range(1, TOTAL_PAGES + 1):
        page_data = scrape_page(page, session)
        all_products.extend(page_data)
        if page < TOTAL_PAGES:
            wait = random.uniform(3, 6)
            print(f"  Waiting {wait:.1f} seconds before next page...")
            time.sleep(wait)

    # Save output to CSV with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"amazon_laptops_{timestamp}.csv"

    df = pd.DataFrame(all_products)
    df.drop_duplicates(subset=["Title"], inplace=True)   # Remove any duplicates
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    # utf-8-sig encoding is used so the ₹ symbol is added
    print(f"  DONE! File saved as: {filename}")
    print(f"  Total unique products collected: {len(df)}")


    #Preview in the terminal
    pd.set_option("display.max_colwidth", 40)
    print("\nPreview of first 5 rows:")
    print(df[["Title", "Price", "Rating", "Result Type"]].head().to_string())

    print("\nAd vs Organic breakdown:")
    print(df["Result Type"].value_counts().to_string())

    rated = (df["Rating"] != "N/A").sum()
    print(f"\n Products with rating : {rated}")
    print(f"Products without     : {len(df) - rated}")
    print("(Blank ratings = newly launched products with 0 reviews on Amazon)")


if __name__ == "__main__":
    main()