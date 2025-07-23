from flask import Blueprint, request, jsonify
import requests
import json
from datetime import datetime
from src.models.stock import Stock, StockPrice, db
from src.services.angel_one_service import AngelOneService
from src.services.news_service import NewsService
from src.services.ai_service import AIService

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/stock/search', methods=['GET'])
def search_stock():
    """Search for stocks by symbol or name"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        angel_service = AngelOneService()
        results = angel_service.search_stocks(query)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/stock/realtime', methods=['GET'])
def get_realtime_stock():
    """Get real-time stock data with AI insights"""
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({'error': 'Symbol parameter is required'}), 400
    
    try:
        # Initialize services
        angel_service = AngelOneService()
        news_service = NewsService()
        ai_service = AIService()
        
        # Fetch stock data
        stock_data = angel_service.get_stock_quote(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        # Fetch news
        news_data = news_service.get_stock_news(symbol)
        
        # Generate AI insight
        ai_insight = ai_service.generate_stock_insight(stock_data, news_data)
        
        # Combine all data
        response_data = {
            'stock_data': stock_data,
            'news': news_data,
            'ai_insight': ai_insight,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/index/scan', methods=['GET'])
def scan_index():
    """Scan index constituents and rank them"""
    index_name = request.args.get('index', 'Nifty50')
    limit = int(request.args.get('limit', 10))
    
    try:
        angel_service = AngelOneService()
        news_service = NewsService()
        ai_service = AIService()
        
        # Get index constituents
        constituents = angel_service.get_index_constituents(index_name)
        
        # Score and rank stocks
        ranked_stocks = []
        for stock_symbol in constituents[:20]:  # Limit to first 20 for performance
            try:
                stock_data = angel_service.get_stock_quote(stock_symbol)
                news_data = news_service.get_stock_news(stock_symbol)
                
                # Calculate score (simplified scoring logic)
                score = ai_service.calculate_stock_score(stock_data, news_data)
                
                ranked_stocks.append({
                    'symbol': stock_symbol,
                    'name': stock_data.get('name', stock_symbol),
                    'price': stock_data.get('price', 0),
                    'change_percent': stock_data.get('change_percent', 0),
                    'score': score,
                    'recommendation': 'buy' if score > 7 else 'hold' if score > 4 else 'sell'
                })
            except Exception as e:
                print(f"Error processing {stock_symbol}: {e}")
                continue
        
        # Sort by score and return top results
        ranked_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'index': index_name,
            'top_stocks': ranked_stocks[:limit],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/ai/recommendations', methods=['GET'])
def get_ai_recommendations():
    """Get AI-powered stock recommendations"""
    count = int(request.args.get('count', 5))
    index_name = request.args.get('index', 'Nifty50')
    
    try:
        angel_service = AngelOneService()
        news_service = NewsService()
        ai_service = AIService()
        
        # Get market context
        market_data = angel_service.get_market_indices()
        
        # Get index constituents
        constituents = angel_service.get_index_constituents(index_name)
        
        # Generate AI recommendations
        recommendations = ai_service.generate_recommendations(
            constituents, market_data, count
        )
        
        return jsonify({
            'recommendations': recommendations,
            'market_context': market_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/ai/query', methods=['POST'])
def ai_query():
    """Handle AI queries about stocks or market"""
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    try:
        angel_service = AngelOneService()
        ai_service = AIService()
        
        # Get market context
        market_data = angel_service.get_market_indices()
        
        # Generate AI response
        response = ai_service.answer_query(question, market_data)
        
        return jsonify({
            'question': question,
            'answer': response,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/market/indices', methods=['GET'])
def get_market_indices():
    """Get market indices and sentiment data"""
    try:
        angel_service = AngelOneService()
        market_data = angel_service.get_market_indices()
        
        return jsonify({
            'indices': market_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

