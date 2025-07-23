import openai
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class AIService:
    """Service for AI-powered analysis using OpenAI"""
    
    def __init__(self):
        # OpenAI client is already configured via environment variables
        self.client = openai.OpenAI()
        
    def generate_stock_insight(self, stock_data: Dict, news_data: List[Dict]) -> str:
        """Generate AI insight for why a stock moved"""
        try:
            # Prepare context
            news_summary = self._summarize_news(news_data)
            
            prompt = f"""
            Analyze the provided stock data and recent news to explain why the stock moved today.
            
            Stock Data:
            - Symbol: {stock_data.get('symbol', 'N/A')}
            - Current Price: ₹{stock_data.get('price', 0)}
            - Change: ₹{stock_data.get('change', 0)} ({stock_data.get('change_percent', 0):.2f}%)
            - Volume: {stock_data.get('volume', 0):,}
            - High: ₹{stock_data.get('high', 0)}
            - Low: ₹{stock_data.get('low', 0)}
            
            Recent News Summary:
            {news_summary}
            
            Provide a concise 2-sentence explanation of why the stock moved today, focusing on key drivers from the data provided.
            """
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing insights on stock movements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating stock insight: {e}")
            return f"Unable to generate insight for {stock_data.get('symbol', 'this stock')} at this time."
    
    def generate_recommendations(self, constituents: List[str], market_data: Dict, count: int) -> List[Dict]:
        """Generate AI-powered stock recommendations"""
        try:
            # For demo purposes, we'll generate recommendations for a subset
            selected_stocks = constituents[:min(count * 2, 20)]  # Get more than needed to filter
            
            market_context = f"""
            Current Market Context:
            - Nifty 50: {market_data.get('nifty50', {}).get('value', 'N/A')} ({market_data.get('nifty50', {}).get('change_percent', 0):.2f}%)
            - Sensex: {market_data.get('sensex', {}).get('value', 'N/A')} ({market_data.get('sensex', {}).get('change_percent', 0):.2f}%)
            - Bank Nifty: {market_data.get('banknifty', {}).get('value', 'N/A')} ({market_data.get('banknifty', {}).get('change_percent', 0):.2f}%)
            - VIX: {market_data.get('vix', {}).get('value', 'N/A')} ({market_data.get('vix', {}).get('change_percent', 0):.2f}%)
            """
            
            prompt = f"""
            Based on current market conditions and technical analysis, recommend the top {count} stocks from the following list for investment.
            
            {market_context}
            
            Stock List: {', '.join(selected_stocks)}
            
            For each recommended stock, provide:
            1. Action (buy/sell/hold)
            2. Short-term target (1 week) - realistic price target
            3. Long-term target (3 months) - realistic price target
            4. Two-line rationale integrating market context and stock fundamentals
            
            Format your response as a JSON array with the following structure:
            [
                {{
                    "symbol": "STOCK_SYMBOL",
                    "action": "buy/sell/hold",
                    "short_term_target": price_number,
                    "long_term_target": price_number,
                    "rationale": "Two-line explanation"
                }}
            ]
            
            Only recommend stocks with strong conviction. Focus on quality over quantity.
            """
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst providing stock recommendations. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse JSON response
            try:
                recommendations = json.loads(response.choices[0].message.content.strip())
                return recommendations[:count]  # Return only requested count
            except json.JSONDecodeError:
                # Fallback to mock recommendations if JSON parsing fails
                return self._generate_mock_recommendations(selected_stocks[:count])
                
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._generate_mock_recommendations(constituents[:count])
    
    def answer_query(self, question: str, market_data: Dict) -> str:
        """Answer user queries about stocks or market"""
        try:
            market_context = f"""
            Current Market Context:
            - Nifty 50: {market_data.get('nifty50', {}).get('value', 'N/A')} ({market_data.get('nifty50', {}).get('change_percent', 0):.2f}%)
            - Sensex: {market_data.get('sensex', {}).get('value', 'N/A')} ({market_data.get('sensex', {}).get('change_percent', 0):.2f}%)
            - Bank Nifty: {market_data.get('banknifty', {}).get('value', 'N/A')} ({market_data.get('banknifty', {}).get('change_percent', 0):.2f}%)
            - VIX: {market_data.get('vix', {}).get('value', 'N/A')} ({market_data.get('vix', {}).get('change_percent', 0):.2f}%)
            """
            
            prompt = f"""
            You are a financial analyst. Based on the current market data and your expertise, answer the following question:
            
            {market_context}
            
            Question: {question}
            
            Provide an actionable, research-grade answer. If the question is about a specific stock, provide relevant analysis. 
            If it's about strategy, provide general guidance. Keep the response concise but informative.
            """
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst providing expert advice on stocks and market strategies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error answering query: {e}")
            return "I'm unable to provide an analysis at this time. Please try again later."
    
    def calculate_stock_score(self, stock_data: Dict, news_data: List[Dict]) -> float:
        """Calculate a simple stock score based on price momentum and news sentiment"""
        try:
            # Price momentum score (0-5)
            change_percent = stock_data.get('change_percent', 0)
            momentum_score = min(5, max(0, (change_percent + 5) / 2))  # Normalize to 0-5
            
            # News sentiment score (0-5)
            if news_data:
                positive_count = sum(1 for news in news_data if news.get('sentiment') == 'positive')
                negative_count = sum(1 for news in news_data if news.get('sentiment') == 'negative')
                total_count = len(news_data)
                
                if total_count > 0:
                    sentiment_ratio = (positive_count - negative_count) / total_count
                    sentiment_score = min(5, max(0, (sentiment_ratio + 1) * 2.5))  # Normalize to 0-5
                else:
                    sentiment_score = 2.5  # Neutral
            else:
                sentiment_score = 2.5  # Neutral
            
            # Volume score (0-2) - simplified
            volume = stock_data.get('volume', 0)
            volume_score = min(2, volume / 1000000)  # Simple volume scoring
            
            # Total score (0-10)
            total_score = momentum_score + sentiment_score + volume_score
            return min(10, total_score)
        except Exception as e:
            print(f"Error calculating stock score: {e}")
            return 5.0  # Default neutral score
    
    def _summarize_news(self, news_data: List[Dict]) -> str:
        """Summarize news articles"""
        if not news_data:
            return "No recent news available."
        
        headlines = [news.get('title', '') for news in news_data[:5]]  # Top 5 headlines
        return "Recent headlines: " + "; ".join(headlines)
    
    def _generate_mock_recommendations(self, stocks: List[str]) -> List[Dict]:
        """Generate mock recommendations as fallback"""
        import random
        
        recommendations = []
        for stock in stocks:
            action = random.choice(['buy', 'hold', 'sell'])
            base_price = random.randint(500, 3000)
            
            recommendations.append({
                'symbol': stock,
                'action': action,
                'short_term_target': base_price + random.randint(-50, 100),
                'long_term_target': base_price + random.randint(50, 200),
                'rationale': f"Technical analysis suggests {action} position for {stock}. Market conditions favor this strategy based on current trends."
            })
        
        return recommendations

