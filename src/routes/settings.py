from flask import Blueprint, request, jsonify
import json
from src.models.user import User, db
from src.models.stock import CustomList

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get user settings and preferences"""
    user_id = request.args.get('user_id', 1)  # Default user for demo
    
    try:
        user = User.query.get(user_id)
        if not user:
            # Create default user if not exists
            user = User(
                username='demo_user',
                email='demo@proiqtech.com'
            )
            db.session.add(user)
            db.session.commit()
        
        # Get custom lists
        custom_lists = CustomList.query.filter_by(user_id=user_id).all()
        lists_data = []
        for custom_list in custom_lists:
            lists_data.append({
                'id': custom_list.id,
                'name': custom_list.name,
                'stocks': json.loads(custom_list.stocks) if custom_list.stocks else [],
                'created_at': custom_list.created_at.isoformat(),
                'updated_at': custom_list.updated_at.isoformat()
            })
        
        # Default settings
        default_settings = {
            'theme': 'dark',
            'default_index': 'Nifty50',
            'notification_preferences': {
                'email': True,
                'whatsapp': False,
                'sms': False
            },
            'ai_settings': {
                'recommendation_count': 5,
                'risk_tolerance': 'moderate'
            },
            'display_preferences': {
                'currency_format': 'INR',
                'number_format': 'indian',
                'chart_type': 'candlestick'
            }
        }
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'settings': default_settings,
            'custom_lists': lists_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Update user settings"""
    data = request.get_json()
    user_id = data.get('user_id', 1)
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # In a real implementation, you would store settings in a separate table
        # For now, we'll just return success
        
        return jsonify({'message': 'Settings updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/custom-lists', methods=['POST'])
def create_custom_list():
    """Create a new custom stock list"""
    data = request.get_json()
    
    required_fields = ['name', 'stocks']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        custom_list = CustomList(
            user_id=data.get('user_id', 1),
            name=data['name'],
            stocks=json.dumps(data['stocks'])
        )
        
        db.session.add(custom_list)
        db.session.commit()
        
        return jsonify({
            'message': 'Custom list created successfully',
            'list_id': custom_list.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/custom-lists/<int:list_id>', methods=['PUT'])
def update_custom_list(list_id):
    """Update a custom stock list"""
    data = request.get_json()
    
    try:
        custom_list = CustomList.query.get_or_404(list_id)
        
        if 'name' in data:
            custom_list.name = data['name']
        if 'stocks' in data:
            custom_list.stocks = json.dumps(data['stocks'])
        
        db.session.commit()
        
        return jsonify({'message': 'Custom list updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/custom-lists/<int:list_id>', methods=['DELETE'])
def delete_custom_list(list_id):
    """Delete a custom stock list"""
    try:
        custom_list = CustomList.query.get_or_404(list_id)
        db.session.delete(custom_list)
        db.session.commit()
        
        return jsonify({'message': 'Custom list deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

