# routes.py
"""
Flask-RESTX API routes for the Star Wars REST API.
Provides endpoints for people, planets, vehicles, and user favorites.
"""

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from models import Favorite, People, Planet, User, Vehicle, db


# --- API Models for Documentation ---

# Person models
person_model_fields = {
    'id': fields.Integer(readonly=True, description='Person unique identifier'),
    'name': fields.String(required=True, description='Person name'),
    'gender': fields.String(description='Person gender'),
    'birth_year': fields.String(description='Birth year'),
    'image_url': fields.String(description='Person image URL')
}

# Planet models
planet_model_fields = {
    'id': fields.Integer(readonly=True, description='Planet unique identifier'),
    'name': fields.String(required=True, description='Planet name'),
    'climate': fields.String(description='Planet climate'),
    'population': fields.String(description='Planet population'),
    'image_url': fields.String(description='Planet image URL')
}

# Vehicle models
vehicle_model_fields = {
    'id': fields.Integer(readonly=True, description='Vehicle unique identifier'),
    'name': fields.String(required=True, description='Vehicle name'),
    'model': fields.String(description='Vehicle model'),
    'manufacturer': fields.String(description='Vehicle manufacturer'),
    'image_url': fields.String(description='Vehicle image URL')
}




# --- PEOPLE NAMESPACE ---
people_ns = Namespace('people', description='Star Wars characters/people operations', path='/api')

person_model = people_ns.model('Person', person_model_fields)

@people_ns.route('/people')
class PeopleList(Resource):
    @people_ns.marshal_list_with(person_model)
    @people_ns.doc('list_people')
    def get(self):
        """Fetch all Star Wars characters"""
        try:
            people = People.query.all()
            return [person.serialize() for person in people]
        except Exception as e:
            people_ns.abort(500, f"Error fetching people: {str(e)}")

@people_ns.route('/people/<int:person_id>')
@people_ns.param('person_id', 'The person identifier')
class PersonResource(Resource):
    @people_ns.marshal_with(person_model)
    @people_ns.doc('get_person')
    @people_ns.response(404, 'Person not found')
    def get(self, person_id):
        """Fetch a character by ID"""
        person = People.query.get(person_id)
        if not person:
            people_ns.abort(404, f"Person with ID {person_id} not found")
        return person.serialize()


# --- PLANETS NAMESPACE ---
planets_ns = Namespace('planets', description='Star Wars planets operations', path='/api')

planet_model = planets_ns.model('Planet', planet_model_fields)

@planets_ns.route('/planets')
class PlanetsList(Resource):
    @planets_ns.marshal_list_with(planet_model)
    @planets_ns.doc('list_planets')
    def get(self):
        """Fetch all Star Wars planets"""
        try:
            planets = Planet.query.all()
            return [planet.serialize() for planet in planets]
        except Exception as e:
            planets_ns.abort(500, f"Error fetching planets: {str(e)}")

@planets_ns.route('/planets/<int:planet_id>')
@planets_ns.param('planet_id', 'The planet identifier')
class PlanetResource(Resource):
    @planets_ns.marshal_with(planet_model)
    @planets_ns.doc('get_planet')
    @planets_ns.response(404, 'Planet not found')
    def get(self, planet_id):
        """Fetch a planet by ID"""
        planet = Planet.query.get(planet_id)
        if not planet:
            planets_ns.abort(404, f"Planet with ID {planet_id} not found")
        return planet.serialize()


# --- VEHICLES NAMESPACE ---
vehicles_ns = Namespace('vehicles', description='Star Wars vehicles operations', path='/api')

vehicle_model = vehicles_ns.model('Vehicle', vehicle_model_fields)

@vehicles_ns.route('/vehicles')
class VehiclesList(Resource):
    @vehicles_ns.marshal_list_with(vehicle_model)
    @vehicles_ns.doc('list_vehicles')
    def get(self):
        """Fetch all Star Wars vehicles"""
        try:
            vehicles = Vehicle.query.all()
            return [vehicle.serialize() for vehicle in vehicles]
        except Exception as e:
            vehicles_ns.abort(500, f"Error fetching vehicles: {str(e)}")

@vehicles_ns.route('/vehicles/<int:vehicle_id>')
@vehicles_ns.param('vehicle_id', 'The vehicle identifier')
class VehicleResource(Resource):
    @vehicles_ns.marshal_with(vehicle_model)
    @vehicles_ns.doc('get_vehicle')
    @vehicles_ns.response(404, 'Vehicle not found')
    def get(self, vehicle_id):
        """Fetch a vehicle by ID"""
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            vehicles_ns.abort(404, f"Vehicle with ID {vehicle_id} not found")
        return vehicle.serialize()



# --- FAVORITES NAMESPACE ---
favorites_ns = Namespace('favorites', description='User favorites operations', path='/api')

# Input models for favorites
favorite_input_model = favorites_ns.model('FavoriteInput', {
    'people_id': fields.Integer(description='ID of favorite character'),
    'planet_id': fields.Integer(description='ID of favorite planet'),
    'vehicle_id': fields.Integer(description='ID of favorite vehicle'),
})

# Favorite models (now that all referenced models are defined)
favorite_model_fields = {
    'id': fields.Integer(readonly=True, description='Favorite unique identifier'),
    'user_id': fields.Integer(readonly=True, description='User ID'),
    'favorite_type': fields.String(readonly=True, description='Type of favorite'),
    'people': fields.Nested(person_model, allow_null=True),
    'planet': fields.Nested(planet_model, allow_null=True),
    'vehicle': fields.Nested(vehicle_model, allow_null=True),
    'created_at': fields.String(readonly=True, description='Creation timestamp')
}
favorite_response_model = favorites_ns.model('Favorite', favorite_model_fields)

# Response models
message_model = favorites_ns.model('Message', {
    'message': fields.String(description='Response message'),
    'success': fields.Boolean(description='Operation success status')
})

@favorites_ns.route('/favorites')
class FavoritesList(Resource):
    @jwt_required()
    @favorites_ns.marshal_list_with(favorite_response_model)
    @favorites_ns.doc('list_favorites', security='jwt')
    @favorites_ns.response(401, 'Authentication required')
    def get(self):
        """Get all favorites for the authenticated user"""
        try:
            user_id = get_jwt_identity()
            favorites = Favorite.query.filter_by(user_id=user_id).all()
            return [favorite.serialize() for favorite in favorites]
        except Exception as e:
            favorites_ns.abort(500, f"Error fetching favorites: {str(e)}")

    @jwt_required()
    @favorites_ns.expect(favorite_input_model)
    @favorites_ns.marshal_with(message_model)
    @favorites_ns.doc('add_favorite', security='jwt')
    @favorites_ns.response(400, 'Bad request - validation error')
    @favorites_ns.response(401, 'Authentication required')
    @favorites_ns.response(409, 'Favorite already exists')
    def post(self):
        """Add a new favorite for the authenticated user"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validate input - exactly one favorite type should be provided
            favorite_types = ['people_id', 'planet_id', 'vehicle_id']
            provided_types = [key for key in favorite_types if data.get(key)]
            
            if len(provided_types) != 1:
                favorites_ns.abort(400, "Exactly one favorite type (people_id, planet_id, or vehicle_id) must be provided")
            
            # Validate that the referenced item exists
            favorite_type = provided_types[0]
            item_id = data.get(favorite_type)
            
            if favorite_type == 'people_id':
                if not People.query.get(item_id):
                    favorites_ns.abort(404, f"Person with ID {item_id} not found")
            elif favorite_type == 'planet_id':
                if not Planet.query.get(item_id):
                    favorites_ns.abort(404, f"Planet with ID {item_id} not found")
            elif favorite_type == 'vehicle_id':
                if not Vehicle.query.get(item_id):
                    favorites_ns.abort(404, f"Vehicle with ID {item_id} not found")
            
            # Check if favorite already exists
            existing_favorite = Favorite.query.filter_by(
                user_id=user_id,
                **{favorite_type: item_id}
            ).first()
            
            if existing_favorite:
                favorites_ns.abort(409, "This item is already in your favorites")
            
            # Create new favorite
            favorite = Favorite(user_id=user_id)
            setattr(favorite, favorite_type, item_id)
            
            db.session.add(favorite)
            db.session.commit()
            
            return {
                'message': 'Favorite added successfully',
                'success': True
            }, 201
            
        except IntegrityError:
            db.session.rollback()
            favorites_ns.abort(409, "This item is already in your favorites")
        except Exception as e:
            db.session.rollback()
            favorites_ns.abort(500, f"Error adding favorite: {str(e)}")

@favorites_ns.route('/favorites/<int:favorite_id>')
@favorites_ns.param('favorite_id', 'The favorite identifier')
class FavoriteResource(Resource):
    @jwt_required()
    @favorites_ns.marshal_with(message_model)
    @favorites_ns.doc('delete_favorite', security='jwt')
    @favorites_ns.response(401, 'Authentication required')
    @favorites_ns.response(404, 'Favorite not found')
    def delete(self, favorite_id):
        """Delete a specific favorite"""
        try:
            user_id = get_jwt_identity()
            favorite = Favorite.query.filter_by(
                id=favorite_id, 
                user_id=user_id
            ).first()
            
            if not favorite:
                favorites_ns.abort(404, "Favorite not found or doesn't belong to you")
            
            db.session.delete(favorite)
            db.session.commit()
            
            return {
                'message': 'Favorite deleted successfully',
                'success': True
            }, 200
            
        except Exception as e:
            db.session.rollback()
            favorites_ns.abort(500, f"Error deleting favorite: {str(e)}")

    @jwt_required()
    @favorites_ns.marshal_with(favorite_response_model)
    @favorites_ns.doc('get_favorite', security='jwt')
    @favorites_ns.response(401, 'Authentication required')
    @favorites_ns.response(404, 'Favorite not found')
    def get(self, favorite_id):
        """Get a specific favorite by ID"""
        try:
            user_id = get_jwt_identity()
            favorite = Favorite.query.filter_by(
                id=favorite_id, 
                user_id=user_id
            ).first()
            
            if not favorite:
                favorites_ns.abort(404, "Favorite not found or doesn't belong to you")
            
            return favorite.serialize()
            
        except Exception as e:
            favorites_ns.abort(500, f"Error fetching favorite: {str(e)}")


# --- ADDITIONAL UTILITY ENDPOINTS ---

# User profile endpoint (bonus)
@favorites_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @favorites_ns.doc('get_profile', security='jwt')
    @favorites_ns.response(401, 'Authentication required')
    def get(self):
        """Get current user profile with favorites summary"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                favorites_ns.abort(404, "User not found")
            
            favorites_summary = {
                'total_favorites': len(user.favorites),
                'people_count': len([f for f in user.favorites if f.people_id]),
                'planets_count': len([f for f in user.favorites if f.planet_id]),
                'vehicles_count': len([f for f in user.favorites if f.vehicle_id]),
            }
            
            return {
                'user': user.serialize(),
                'favorites_summary': favorites_summary
            }
            
        except Exception as e:
            favorites_ns.abort(500, f"Error fetching profile: {str(e)}")


# Configure JWT security for Swagger documentation
authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}