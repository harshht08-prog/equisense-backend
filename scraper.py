import yfinance as yf
import json

def get_stock_news(ticker_symbol):
    """
    Fetches and normalizes news data.
    """
    print(f"Fetching news for {ticker_symbol}...")
    stock = yf.Ticker(ticker_symbol)
    raw_news = stock.news
    
    # This list will hold our clean data objects
    clean_news = []
    
    for article in raw_news:
        # 1. Try to grab the 'content' object (where the data hides)
        #    If it doesn't exist, default to the article itself (fallback)
        content = article.get('content', article)
        
        # 2. Extract title
        title = content.get('title')
        
        # 3. Extract link. 
        #    Sometimes it's 'clickThroughUrl', sometimes 'canonicalUrl'
        #    We traverse safely using .get() to avoid crashing on missing keys
        link_data = content.get('clickThroughUrl') or content.get('canonicalUrl')
        link = link_data.get('url') if link_data else None
        
        # 4. Extract logic: Only keep items that have both a title and a link
        if title and link:
            clean_news.append({
                "id": article.get('id'), # Good for React 'key' props!
                "title": title,
                "url": link,
                "published": content.get('pubDate')
            })
            
    return clean_news

def save_to_json(news_data):
    """
    Saves the data to a file, acting like a local database.
    """
    filename = 'news.json'
    with open(filename, 'w') as f:
        # json.dump is the Python equivalent of JSON.stringify()
        # indent=2 makes it pretty-printed (readable)
        json.dump(news_data, f, indent=2)
    
    print(f"Successfully saved {len(news_data)} articles to {filename}")

# --- Main Execution ---
if __name__ == "__main__":
    ticker = "META"
    news = get_stock_news(ticker)
    save_to_json(news)