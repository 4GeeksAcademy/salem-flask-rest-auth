# routes.py
# This file contains all route registrations and route logic for the Flask app.

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, People, Planet, Vehicle, Favorite


def register_routes(app):

    @app.route('/api/users/favorites', methods=['GET'])
    @jwt_required()
    def users_favorites():
        user_id = get_jwt_identity()
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        return jsonify([f.serialize() for f in favorites])
    # Auth routes
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'msg': 'Email and password required'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'msg': 'User already exists'}), 409
        user = User(email=email, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg': 'User registered successfully'})

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'msg': 'Invalid credentials'}), 401
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'user': user.serialize()})

    # Example protected route
    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def profile():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        return jsonify(user.serialize())

    # CRUD for People
    @app.route('/api/people', methods=['GET'])
    def get_people():
        people = People.query.all()
        return jsonify([p.serialize() for p in people])

    @app.route('/api/people/<int:person_id>', methods=['GET'])
    def get_person(person_id):
        person = People.query.get(person_id)
        if not person:
            return jsonify({'msg': 'Person not found'}), 404
        return jsonify(person.serialize())

    # CRUD for Planets
    @app.route('/api/planets', methods=['GET'])
    def get_planets():
        planets = Planet.query.all()
        return jsonify([p.serialize() for p in planets])

    @app.route('/api/planets/<int:planet_id>', methods=['GET'])
    def get_planet(planet_id):
        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({'msg': 'Planet not found'}), 404
        return jsonify(planet.serialize())

    # CRUD for Vehicles
    @app.route('/api/vehicles', methods=['GET'])
    def get_vehicles():
        vehicles = Vehicle.query.all()
        return jsonify([v.serialize() for v in vehicles])

    @app.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
    def get_vehicle(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'msg': 'Vehicle not found'}), 404
        return jsonify(vehicle.serialize())

    # Favorites routes (add/remove/list)
    @app.route('/api/favorites', methods=['GET'])
    @jwt_required()
    def get_favorites():
        user_id = get_jwt_identity()
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        return jsonify([f.serialize() for f in favorites])

    @app.route('/api/favorites', methods=['POST'])
    @jwt_required()
    def add_favorite():
        user_id = get_jwt_identity()
        data = request.get_json()
        favorite = Favorite(user_id=user_id,
                            people_id=data.get('people_id'),
                            planet_id=data.get('planet_id'),
                            vehicle_id=data.get('vehicle_id'))
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'msg': 'Favorite added'})

    @app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
    @jwt_required()
    def delete_favorite(favorite_id):
        user_id = get_jwt_identity()
        favorite = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()
        if not favorite:
            return jsonify({'msg': 'Favorite not found'}), 404
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'msg': 'Favorite deleted'})
