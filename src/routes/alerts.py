from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.stock import Alert, Stock, db
from src.models.user import User

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts for a user"""
    user_id = request.args.get('user_id', 1)  # Default user for demo
    
    try:
        alerts = Alert.query.filter_by(user_id=user_id).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'stock_symbol': alert.stock.symbol if alert.stock else 'Unknown',
                'trigger_type': alert.trigger_type,
                'trigger_value': alert.trigger_value,
                'notification_channel': alert.notification_channel,
                'status': alert.status,
                'created_at': alert.created_at.isoformat(),
                'triggered_at': alert.triggered_at.isoformat() if alert.triggered_at else None
            })
        
        return jsonify({
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts', methods=['POST'])
def create_alert():
    """Create a new alert"""
    data = request.get_json()
    
    required_fields = ['stock_symbol', 'trigger_type', 'trigger_value', 'notification_channel']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Find or create stock
        stock = Stock.query.filter_by(symbol=data['stock_symbol']).first()
        if not stock:
            stock = Stock(
                symbol=data['stock_symbol'],
                name=data.get('stock_name', data['stock_symbol']),
                exchange='NSE'
            )
            db.session.add(stock)
            db.session.flush()
        
        # Create alert
        alert = Alert(
            user_id=data.get('user_id', 1),  # Default user for demo
            stock_id=stock.id,
            trigger_type=data['trigger_type'],
            trigger_value=data['trigger_value'],
            notification_channel=data['notification_channel'],
            webhook_url=data.get('webhook_url'),
            status='active'
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'message': 'Alert created successfully',
            'alert_id': alert.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """Update an alert"""
    data = request.get_json()
    
    try:
        alert = Alert.query.get_or_404(alert_id)
        
        # Update fields
        if 'trigger_value' in data:
            alert.trigger_value = data['trigger_value']
        if 'notification_channel' in data:
            alert.notification_channel = data['notification_channel']
        if 'webhook_url' in data:
            alert.webhook_url = data['webhook_url']
        if 'status' in data:
            alert.status = data['status']
        
        db.session.commit()
        
        return jsonify({'message': 'Alert updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    try:
        alert = Alert.query.get_or_404(alert_id)
        db.session.delete(alert)
        db.session.commit()
        
        return jsonify({'message': 'Alert deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/trigger', methods=['POST'])
def trigger_alert():
    """Manually trigger an alert (for testing)"""
    data = request.get_json()
    alert_id = data.get('alert_id')
    
    if not alert_id:
        return jsonify({'error': 'alert_id is required'}), 400
    
    try:
        alert = Alert.query.get_or_404(alert_id)
        
        # Update alert status
        alert.status = 'triggered'
        alert.triggered_at = datetime.utcnow()
        db.session.commit()
        
        # Here you would integrate with Zapier/Make to send actual notifications
        # For now, we'll just return a success message
        
        return jsonify({
            'message': 'Alert triggered successfully',
            'alert_id': alert_id,
            'notification_sent': True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

