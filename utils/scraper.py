import re
import logging
import httpx

logger = logging.getLogger(__name__)

async def fetch_price(url: str) -> str:
    """
    Main entry point for scraping. Routes the URL to the appropriate scraper.
    """
    if "digikala.com" in url:
        return await _scrape_digikala_api(url)
    
    # Placeholder for other websites using BeautifulSoup in the future
    return "❌ Scraping for this domain is not supported yet."

async def _scrape_digikala_api(url: str) -> str:
    """
    Extracts the product price using Digikala's public JSON API.
    Bypasses HTML parsing and JavaScript rendering for maximum speed.
    """
    # Extract the DKP ID using Regex
    match = re.search(r"dkp-(\d+)", url, re.IGNORECASE)
    if not match:
        return "❌ Could not extract the product ID from the URL."
    
    product_id = match.group(1)
    api_endpoint = f"https://api.digikala.com/v2/product/{product_id}/"

    # Fake browser headers to bypass basic anti-bot protection
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }
    
    try:
        # Use httpx.AsyncClient for non-blocking network requests
        async with httpx.AsyncClient() as client:
            response = await client.get(api_endpoint, headers=headers, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Safely navigate the JSON dictionary
            product_data = data.get("data", {}).get("product", {})
            status = product_data.get("status")
            
            if status != "marketable":
                return "⚠️ This product is currently out of stock or unavailable."
            
            # Digikala stores the active price in the default_variant object
            default_variant = product_data.get("default_variant", {})
            price = default_variant.get("price", {}).get("selling_price")
            
            if price:
                # Format price with commas (e.g., 1,500,000)
                return f"✅ Current Price: {price:,} Tomans"
            
            return "❌ Price not found in the product data."
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP Error while connecting to Digikala API: {e}")
        return "❌ Connection error while trying to fetch data from the store."
    except Exception as e:
        logger.error(f"Unexpected error in scraper: {e}")
        return "❌ An unexpected error occurred while processing the price."