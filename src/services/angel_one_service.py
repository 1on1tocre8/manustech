import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class AngelOneService:
    """Service for interacting with Angel One SmartAPI"""
    
    def __init__(self):
        self.base_url = "https://apiconnect.angelbroking.com"
        self.api_key = os.getenv('ANGEL_ONE_API_KEY', '')
        self.client_id = os.getenv('ANGEL_ONE_CLIENT_ID', '')
        self.access_token = os.getenv('ANGEL_ONE_ACCESS_TOKEN', '')
        self.refresh_token = os.getenv('ANGEL_ONE_REFRESH_TOKEN', '')
        
        # Mock data for development/testing
        self.mock_mode = False  # Set to False when real API keys are available
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '127.0.0.1',
            'X-ClientPublicIP': '127.0.0.1',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': self.api_key
        }
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by symbol or name"""
        if self.mock_mode:
            return self._mock_search_stocks(query)
        
        url = f"{self.base_url}/rest/secure/angelbroking/market/v1/search"
        payload = {"searchscrip": query}
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            print(f"Error searching stocks: {e}")
            return []
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time stock quote"""
        if self.mock_mode:
            return self._mock_stock_quote(symbol)
        
        url = f"{self.base_url}/rest/secure/angelbroking/market/v1/quote"
        payload = {
            "mode": "FULL",
            "exchangeTokens": {
                "NSE": [symbol]
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('fetched', [{}])[0] if data.get('data') else None
        except Exception as e:
            print(f"Error getting stock quote: {e}")
            return None
    
    def get_index_constituents(self, index_name: str) -> List[str]:
        """Get constituents of an index"""
        if self.mock_mode:
            return self._mock_index_constituents(index_name)
        
        # This would require a specific endpoint for index constituents
        # For now, returning mock data
        return self._mock_index_constituents(index_name)
    
    def get_market_indices(self) -> Dict:
        """Get market indices data"""
        if self.mock_mode:
            return self._mock_market_indices()
        
        # Implementation for real API would go here
        return self._mock_market_indices()
    
    # Mock data methods for development
    def _mock_search_stocks(self, query: str) -> List[Dict]:
        """Mock stock search results"""
        mock_stocks = [
            {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "exchange": "NSE"},
            {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "exchange": "NSE"},
            {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "exchange": "NSE"},
            {"symbol": "INFY", "name": "Infosys Ltd", "exchange": "NSE"},
            {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "exchange": "NSE"}
        ]
        
        return [stock for stock in mock_stocks if query.upper() in stock["symbol"] or query.upper() in stock["name"].upper()]
    
    def _mock_stock_quote(self, symbol: str) -> Dict:
        """Mock stock quote data"""
        import random
        
        base_prices = {
            "RELIANCE": 2500,
            "TCS": 3200,
            "HDFCBANK": 1600,
            "INFY": 1400,
            "ICICIBANK": 900,
            "WIPRO": 400,
            "LT": 2000,
            "SBIN": 500,
            "BHARTIARTL": 800,
            "ITC": 450
        }
        
        base_price = base_prices.get(symbol, 1000)
        current_price = base_price + random.uniform(-50, 50)
        change = current_price - base_price
        change_percent = (change / base_price) * 100
        
        return {
            "symbol": symbol,
            "name": f"{symbol} Ltd",
            "price": round(current_price, 2),
            "open": round(base_price + random.uniform(-20, 20), 2),
            "high": round(current_price + random.uniform(0, 30), 2),
            "low": round(current_price - random.uniform(0, 30), 2),
            "close": round(current_price, 2),
            "volume": random.randint(100000, 10000000),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _mock_index_constituents(self, index_name: str) -> List[str]:
        """Mock index constituents"""
        nifty50_stocks = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "KOTAKBANK", "HINDUNILVR",
            "LT", "SBIN", "BHARTIARTL", "ITC", "ASIANPAINT", "AXISBANK", "MARUTI", "BAJFINANCE",
            "HCLTECH", "WIPRO", "ULTRACEMCO", "NESTLEIND", "DMART", "BAJAJFINSV", "TITAN",
            "ADANIPORTS", "ONGC", "NTPC", "POWERGRID", "M&M", "TECHM", "SUNPHARMA", "TATAMOTORS",
            "COALINDIA", "INDUSINDBK", "GRASIM", "CIPLA", "EICHERMOT", "HEROMOTOCO", "DRREDDY",
            "JSWSTEEL", "BRITANNIA", "APOLLOHOSP", "DIVISLAB", "BPCL", "TATACONSUM", "HINDALCO",
            "BAJAJ-AUTO", "SHREECEM", "UPL", "TATASTEEL", "ADANIENT", "SBILIFE"
        ]
        
        bank_nifty_stocks = [
            "HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "AXISBANK", "INDUSINDBK",
            "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "PNB", "AUBANK", "RBLBANK"
        ]
        
        if index_name.upper() == "NIFTY50":
            return nifty50_stocks
        elif index_name.upper() == "BANKNIFTY":
            return bank_nifty_stocks
        else:
            return nifty50_stocks[:10]  # Default to top 10 Nifty stocks
    
    def _mock_market_indices(self) -> Dict:
        """Mock market indices data"""
        import random
        
        return {
            "nifty50": {
                "value": round(19500 + random.uniform(-200, 200), 2),
                "change": round(random.uniform(-100, 100), 2),
                "change_percent": round(random.uniform(-1, 1), 2)
            },
            "sensex": {
                "value": round(65000 + random.uniform(-500, 500), 2),
                "change": round(random.uniform(-300, 300), 2),
                "change_percent": round(random.uniform(-1, 1), 2)
            },
            "banknifty": {
                "value": round(44000 + random.uniform(-400, 400), 2),
                "change": round(random.uniform(-200, 200), 2),
                "change_percent": round(random.uniform(-1, 1), 2)
            },
            "vix": {
                "value": round(15 + random.uniform(-3, 3), 2),
                "change": round(random.uniform(-1, 1), 2),
                "change_percent": round(random.uniform(-5, 5), 2)
            }
        }

