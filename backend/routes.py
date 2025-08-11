# routes.py
# This file contains all route registrations and route logic for the Flask app.

from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import Favorite, People, Planet, User, Vehicle, db


def register_routes(app):

    # Example protected route
    @app.route("/api/profile", methods=["GET"], endpoint="profile_api")
    @jwt_required()
    def profile():
        """
        Get user profile
        ---
        tags:
            - User
        security:
            - Bearer: []
        responses:
            200:
                description: User profile
            404:
                description: User not found
        """
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"msg": "Missing or invalid JWT"}), 401
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        # Context7 best practice: return a complete, API-friendly user payload
        return jsonify(user.serialize()), 200

    # CRUD for People
    @app.route("/api/people", methods=["GET"], endpoint="get_people_api")
    def get_people():
        """
        Get all people
        ---
        tags:
            - People
        responses:
            200:
                description: List of people
        """
        people = People.query.all()
        return jsonify([p.serialize() for p in people])

    @app.route(
        "/api/people/<int:person_id>", methods=["GET"], endpoint="get_person_api"
    )
    def get_person(person_id):
        """
        Get person by ID
        ---
        tags:
            - People
        parameters:
            - in: path
                name: person_id
                type: integer
                required: true
        responses:
            200:
                description: Person found
            404:
                description: Person not found
        """
        person = People.query.get(person_id)
        if not person:
            return jsonify({"msg": "Person not found"}), 404
        return jsonify(person.serialize())

    # CRUD for Planets
    @app.route("/api/planets", methods=["GET"], endpoint="get_planets_api")
    def get_planets():
        """
        Get all planets
        ---
        tags:
            - Planets
        responses:
            200:
                description: List of planets
        """
        planets = Planet.query.all()
        return jsonify([p.serialize() for p in planets])

    @app.route(
        "/api/planets/<int:planet_id>", methods=["GET"], endpoint="get_planet_api"
    )
    def get_planet(planet_id):
        """
        Get planet by ID
        ---
        tags:
            - Planets
        parameters:
            - in: path
                name: planet_id
                type: integer
                required: true
        responses:
            200:
                description: Planet found
            404:
                description: Planet not found
        """
        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({"msg": "Planet not found"}), 404
        return jsonify(planet.serialize())

    # CRUD for Vehicles
    @app.route("/api/vehicles", methods=["GET"], endpoint="get_vehicles_api")
    def get_vehicles():
        """
        Get all vehicles
        ---
        tags:
            - Vehicles
        responses:
            200:
                description: List of vehicles
        """
        vehicles = Vehicle.query.all()
        return jsonify([v.serialize() for v in vehicles])

    @app.route(
        "/api/vehicles/<int:vehicle_id>", methods=["GET"], endpoint="get_vehicle_api"
    )
    def get_vehicle(vehicle_id):
        """
        Get vehicle by ID
        ---
        tags:
            - Vehicles
        parameters:
            - in: path
                name: vehicle_id
                type: integer
                required: true
        responses:
            200:
                description: Vehicle found
            404:
                description: Vehicle not found
        """
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"msg": "Vehicle not found"}), 404
        return jsonify(vehicle.serialize())

    # Favorites routes (add/remove/list)
    @app.route("/api/favorites", methods=["GET"], endpoint="get_favorites_api")
    @jwt_required()
    def get_favorites():
        """
        Get all favorites for user
        ---
        tags:
            - Favorites
        security:
            - Bearer: []
        responses:
            200:
                description: List of favorites
        """
        user_id = get_jwt_identity()
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        return jsonify([f.serialize() for f in favorites])

    @app.route("/api/favorites", methods=["POST"], endpoint="add_favorite_api")
    @jwt_required()
    def add_favorite():
        """
        Add a favorite
        ---
        tags:
            - Favorites
        security:
            - Bearer: []
        parameters:
            - in: body
                name: body
                schema:
                    type: object
                    properties:
                        people_id:
                            type: integer
                        planet_id:
                            type: integer
                        vehicle_id:
                            type: integer
        responses:
            200:
                description: Favorite added
        """
        user_id = get_jwt_identity()
        data = request.get_json()
        favorite = Favorite()
        favorite.user_id = user_id
        favorite.people_id = data.get("people_id")
        favorite.planet_id = data.get("planet_id")
        favorite.vehicle_id = data.get("vehicle_id")
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite added"})

    @app.route(
        "/api/favorites/<int:favorite_id>",
        methods=["DELETE"],
        endpoint="delete_favorite_api",
    )
    @jwt_required()
    def delete_favorite(favorite_id):
        """
        Delete a favorite
        ---
        tags:
            - Favorites
        security:
            - Bearer: []
        parameters:
            - in: path
                name: favorite_id
                type: integer
                required: true
        responses:
            200:
                description: Favorite deleted
            404:
                description: Favorite not found
        """
        user_id = get_jwt_identity()
        favorite = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()
        if not favorite:
            return jsonify({"msg": "Favorite not found"}), 404
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite deleted"})
