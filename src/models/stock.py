from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    exchange = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StockPrice(db.Model):
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    stock = db.relationship('Stock', backref=db.backref('prices', lazy=True))

class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # buy/sell/hold
    short_term_target = db.Column(db.Float)
    long_term_target = db.Column(db.Float)
    rationale = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('recommendations', lazy=True))
    stock = db.relationship('Stock', backref=db.backref('recommendations', lazy=True))

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    trigger_type = db.Column(db.String(20), nullable=False)  # price/news/ai_recommendation
    trigger_value = db.Column(db.String(100))
    notification_channel = db.Column(db.String(20), nullable=False)  # whatsapp/email/sms
    webhook_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')  # active/triggered/inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    triggered_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('alerts', lazy=True))
    stock = db.relationship('Stock', backref=db.backref('alerts', lazy=True))

class CustomList(db.Model):
    __tablename__ = 'custom_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    stocks = db.Column(db.Text)  # JSON string of stock symbols
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('custom_lists', lazy=True))

