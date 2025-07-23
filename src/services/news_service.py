import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List

class NewsService:
    """Service for fetching news from NewsAPI"""
    
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY', '')
        self.base_url = "https://newsapi.org/v2"
        
        # Mock mode for development
        self.mock_mode = False  # Set to False when real API key is available
    
    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get news articles for a specific stock"""
        if self.mock_mode:
            return self._mock_stock_news(symbol, limit)
        
        # Calculate date range (last 7 days)
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=7)
        
        url = f"{self.base_url}/everything"
        params = {
            'q': f'{symbol} OR "{symbol}"',
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'pageSize': limit,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', ''))
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def get_market_news(self, limit: int = 20) -> List[Dict]:
        """Get general market news"""
        if self.mock_mode:
            return self._mock_market_news(limit)
        
        url = f"{self.base_url}/everything"
        params = {
            'q': 'stock market OR NSE OR BSE OR Nifty OR Sensex',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', ''))
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching market news: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['gain', 'rise', 'up', 'positive', 'growth', 'profit', 'bull', 'surge', 'rally', 'strong']
        negative_words = ['fall', 'drop', 'down', 'negative', 'loss', 'bear', 'decline', 'weak', 'crash', 'plunge']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    # Mock data methods for development
    def _mock_stock_news(self, symbol: str, limit: int) -> List[Dict]:
        """Mock news data for a stock"""
        import random
        
        mock_headlines = [
            f"{symbol} reports strong quarterly earnings, beats estimates",
            f"{symbol} announces new product launch, shares rally",
            f"Analysts upgrade {symbol} target price on positive outlook",
            f"{symbol} faces regulatory challenges, stock under pressure",
            f"Institutional investors increase stake in {symbol}",
            f"{symbol} management provides optimistic guidance for next quarter",
            f"Market volatility affects {symbol} trading volumes",
            f"{symbol} declares dividend, ex-date announced",
            f"Brokerage firms maintain buy rating on {symbol}",
            f"{symbol} stock hits 52-week high on strong fundamentals"
        ]
        
        articles = []
        for i in range(min(limit, len(mock_headlines))):
            headline = random.choice(mock_headlines)
            sentiment = random.choice(['positive', 'negative', 'neutral'])
            
            articles.append({
                'title': headline,
                'description': f"Detailed analysis of {symbol} performance and market outlook...",
                'url': f"https://example.com/news/{symbol.lower()}-{i+1}",
                'source': random.choice(['Economic Times', 'Business Standard', 'Moneycontrol', 'LiveMint']),
                'published_at': (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'sentiment': sentiment
            })
        
        return articles
    
    def _mock_market_news(self, limit: int) -> List[Dict]:
        """Mock general market news"""
        import random
        
        mock_headlines = [
            "Nifty 50 closes higher on positive global cues",
            "Banking stocks lead market rally amid rate cut expectations",
            "FII inflows boost market sentiment, Sensex gains 200 points",
            "IT stocks under pressure on rupee appreciation",
            "Auto sector shows strong performance on festive demand",
            "Market volatility expected ahead of RBI policy announcement",
            "Pharma stocks rally on export order wins",
            "Energy stocks decline on crude oil price concerns",
            "Small-cap stocks outperform large-cap indices",
            "Market experts recommend defensive strategy amid global uncertainty"
        ]
        
        articles = []
        for i in range(min(limit, len(mock_headlines))):
            headline = random.choice(mock_headlines)
            sentiment = random.choice(['positive', 'negative', 'neutral'])
            
            articles.append({
                'title': headline,
                'description': "Comprehensive market analysis and expert opinions on current trends...",
                'url': f"https://example.com/market-news/{i+1}",
                'source': random.choice(['Economic Times', 'Business Standard', 'Moneycontrol', 'LiveMint']),
                'published_at': (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'sentiment': sentiment
            })
        
        return articles

