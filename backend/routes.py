from flask import jsonify, request, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, People, Planet, Vehicle, Favorite
from jwt_utils import jwt_required_custom, get_current_user

def get_authenticated_user():
    """Helper to get current authenticated user from JWT or session"""
    # Try JWT first
    user = get_current_user()
    if user:
        return user, None, None
    
    # Fall back to session-based auth for backward compatibility
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({"msg": "Authentication required"}), 401
    
    user = User.query.get(user_id)
    if not user:
        return None, jsonify({"msg": "User not found"}), 404
    
    return user, None, None

def handle_favorite_action(entity_type, entity_id, action):
    """Generic handler for favorite add/remove operations"""
    user, error_response, status_code = get_authenticated_user()
    if error_response:
        return error_response, status_code
    
    # Get the entity model and field name
    models = {'planet': (Planet, 'planet_id'), 'people': (People, 'people_id'), 'vehicle': (Vehicle, 'vehicle_id')}
    model_class, field_name = models[entity_type]
    
    entity = model_class.query.get_or_404(entity_id)
    filter_kwargs = {'user_id': user.id, field_name: entity.id}
    existing = Favorite.query.filter_by(**filter_kwargs).first()
    
    if action == 'add':
        if existing:
            return jsonify({"msg": f"{entity_type.title()} already in favorites"}), 400
        fav = Favorite(user_id=user.id, **{field_name: entity.id})
        db.session.add(fav)
        db.session.commit()
        return jsonify(fav.serialize()), 201
    
    elif action == 'remove':
        if not existing:
            return jsonify({"msg": f"{entity_type.title()} not in favorites"}), 404
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"msg": f"{entity_type.title()} removed from favorites"}), 200

def handle_entity_request(entity_type, entity_id=None):
    """Generic handler for entity GET requests"""
    models = {'people': People, 'planets': Planet, 'vehicles': Vehicle}
    model_class = models[entity_type]
    
    if entity_id:
        entity = model_class.query.get_or_404(entity_id)
        return jsonify(entity.serialize()), 200
    else:
        entities = model_class.query.all()
        return jsonify([e.serialize() for e in entities]), 200

def register_routes(app):
    
    # Authentication endpoints
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"msg": "Email and password are required"}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({"msg": "Invalid email or password"}), 401
        
        # Check password using bcrypt for new hashed passwords, fallback to plain text
        password_valid = False
        try:
            password_valid = user.check_password(data['password'])
        except:
            # Fallback to plain text comparison for existing users
            password_valid = (user.password == data['password'])
        
        if not password_valid:
            return jsonify({"msg": "Invalid email or password"}), 401
        
        if not user.is_active:
            return jsonify({"msg": "Account is deactivated"}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        # Also store user in session for backward compatibility
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        return jsonify({
            "msg": "Login successful",
            "access_token": access_token,
            "user": user.serialize()
        }), 200
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"msg": "Email and password are required"}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"msg": "Email already registered"}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            is_active=True
        )
        user.set_password(data['password'])
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create JWT token
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                "msg": "User registered successfully",
                "access_token": access_token,
                "user": user.serialize()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Registration failed"}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({"msg": "Logout successful"}), 200
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required_custom(optional=True)
    def get_current_user():
        user, error_response, status_code = get_authenticated_user()
        if error_response:
            return error_response, status_code
        return jsonify({"user": user.serialize()}), 200

    # Star Wars entity endpoints
    @app.route('/api/people', methods=['GET'])
    def get_people():
        return handle_entity_request('people')

    @app.route('/api/people/<int:people_id>', methods=['GET'])
    def get_person(people_id):
        return handle_entity_request('people', people_id)

    @app.route('/api/planets', methods=['GET'])
    def get_planets():
        return handle_entity_request('planets')

    @app.route('/api/planets/<int:planet_id>', methods=['GET'])
    def get_planet(planet_id):
        return handle_entity_request('planets', planet_id)

    @app.route('/api/vehicles', methods=['GET'])
    def get_vehicles():
        return handle_entity_request('vehicles')

    @app.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
    def get_vehicle(vehicle_id):
        return handle_entity_request('vehicles', vehicle_id)

    @app.route('/api/users/favorites', methods=['GET'])
    @jwt_required_custom(optional=True)
    def get_user_favorites():
        user, error_response, status_code = get_authenticated_user()
        if error_response:
            return error_response, status_code
        return jsonify([fav.serialize() for fav in user.favorites]), 200

    # Favorite endpoints
    @app.route('/api/favorite/planet/<int:planet_id>', methods=['POST'])
    @jwt_required_custom(optional=True)
    def add_favorite_planet(planet_id):
        return handle_favorite_action('planet', planet_id, 'add')

    @app.route('/api/favorite/people/<int:people_id>', methods=['POST'])
    @jwt_required_custom(optional=True)
    def add_favorite_people(people_id):
        return handle_favorite_action('people', people_id, 'add')

    @app.route('/api/favorite/vehicle/<int:vehicle_id>', methods=['POST'])
    @jwt_required_custom(optional=True)
    def add_favorite_vehicle(vehicle_id):
        return handle_favorite_action('vehicle', vehicle_id, 'add')

    @app.route('/api/favorite/planet/<int:planet_id>', methods=['DELETE'])
    @jwt_required_custom(optional=True)
    def remove_favorite_planet(planet_id):
        return handle_favorite_action('planet', planet_id, 'remove')

    @app.route('/api/favorite/people/<int:people_id>', methods=['DELETE'])
    @jwt_required_custom(optional=True)
    def remove_favorite_people(people_id):
        return handle_favorite_action('people', people_id, 'remove')

    @app.route('/api/favorite/vehicle/<int:vehicle_id>', methods=['DELETE'])
    @jwt_required_custom(optional=True)
    def remove_favorite_vehicle(vehicle_id):
        return handle_favorite_action('vehicle', vehicle_id, 'remove')
