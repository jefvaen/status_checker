import requests, os
from bs4 import BeautifulSoup


in_stock_webhook = os.getenv("in_stock_webhook") 
logging_webhook  = os.getenv("logging_webhook")  

aa_url = 'https://aa-drink.com/shop/cycling'
product_to_check = 'Massage gun'


def check_stock_status(product_to_check):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    try:
        response = requests.get(aa_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching the page: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Search all product blocks
    products = soup.find_all(class_='bwx-card')
    for product in products:
        title_tag = product.find('h3')

        if title_tag and product_to_check.lower() in title_tag.get_text(strip=True).lower():
            stock_warning = product.find(class_='stock-warning bwx-text-primary')
            if stock_warning:
                return stock_warning.get_text(strip=True)
            else:
                return "available"


def notify_discord(data, web_hook):

    response = requests.post(web_hook, json=data)
    if response.status_code != 204:
        print("Failed to send Discord message:", response.text)


if __name__ == "__main__":
    
    in_stock_status = check_stock_status(product_to_check)
    
    if in_stock_status is None:
        in_stock_status = "Product not found"
    
    # log the status: 
    data = {"content": f"**Checking for Product**:\n➡️ {product_to_check}\n➡️ status: {in_stock_status}"}
    notify_discord(data, logging_webhook)
    print(data)
    
    #  back in stock!!
    if in_stock_status == "available" : 
       data = {"content": f"🚨 **Product Back In Stock!**\n{product_to_check}"}
       notify_discord(data, in_stock_webhook)
       print(data)
    
    # alert!! 
    if in_stock_status == "Product not found" :
        data = {"content": f"🚨 **Error - Product does not exist!**\n{product_to_check}"}
        notify_discord(data, in_stock_webhook)
        print(data)