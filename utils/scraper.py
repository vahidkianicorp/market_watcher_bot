import re
import logging
import httpx

logger = logging.getLogger(__name__)

async def fetch_price(url: str) -> dict:
    """
    Main entry point for scraping. Returns a dictionary with status and data.
    """
    if "digikala.com" in url:
        return await _scrape_digikala_api(url)
    
    return {"success": False, "error_key": "err_not_found"}

async def _scrape_digikala_api(url: str) -> dict:
    """
    Extracts the product price using Digikala's public JSON API.
    Bypasses HTML parsing and JavaScript rendering for maximum speed.
    """
    # Extract the DKP ID using Regex
    match = re.search(r"dkp-(\d+)", url, re.IGNORECASE)
    if not match:
        return {"success": False, "error_key": "err_not_found"}
    
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
                return {"success": False, "error_key": "err_out_of_stock"}
            
            # Digikala stores the active price in the default_variant object
            default_variant = product_data.get("default_variant", {})
            price = default_variant.get("price", {}).get("selling_price")
            
            if price:
                price_in_tomans = int(price) // 10
                # Return raw formatted number
                return {"success": True, "price": f"{price_in_tomans:,}"}
                
            return {"success": False, "error_key": "err_no_price"}
            
    except httpx.HTTPError as e:
        logger.error(f"API HTTP Error: {e}")
        return {"success": False, "error_key": "err_connection"}