"""Flask-Admin configuration and custom model views for the Star Wars API backend."""
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, People, Planet, Vehicle, Favorite
from markupsafe import Markup
from wtforms import PasswordField
from wtforms.validators import DataRequired

class UserView(ModelView):
    """Custom ModelView for User model with proper password handling"""
    column_exclude_list = ['password']
    form_excluded_columns = ['password']

    def scaffold_form(self):
        """Customize the form to include a password field."""
        form_class = super().scaffold_form()
        form_class.password = PasswordField('Password', [DataRequired()])
        return form_class

    def on_model_change(self, form, model, is_created):
        """Hash the password before saving the user model."""
        if form.password.data:
            model.set_password(form.password.data)

class ImageModelView(ModelView):
    """Custom ModelView for models with image URLs"""
    @staticmethod
    def _list_thumbnail(_, __, model, ___):
        """Render a thumbnail for image_url fields in the admin list view."""
        if model.image_url:
            return Markup(f'<img src="{model.image_url}" style="max-width: 80px; max-height: 80px;">')
        return ''

    column_formatters = {
        'image_url': _list_thumbnail
    }

class PeopleView(ImageModelView):
    column_list = ['name', 'gender', 'birth_year', 'image_url']
    column_labels = {'image_url': 'Image Preview'}
    form_columns = ['name', 'gender', 'birth_year', 'image_url']

class PlanetView(ImageModelView):
    column_list = ['name', 'climate', 'population', 'image_url']
    column_labels = {'image_url': 'Image Preview'}
    form_columns = ['name', 'climate', 'population', 'image_url']

class VehicleView(ImageModelView):
    column_list = ['name', 'model', 'manufacturer', 'image_url']
    column_labels = {'image_url': 'Image Preview'}
    form_columns = ['name', 'model', 'manufacturer', 'image_url']

class FavoriteView(ModelView):
    column_list = ['user.email', 'people.name', 'planet.name', 'vehicle.name']
    column_labels = {
        'user.email': 'User Email',
        'people.name': 'Favorite Character', 
        'planet.name': 'Favorite Planet',
        'vehicle.name': 'Favorite Vehicle'
    }

def setup_admin(app):
    """Configure and initialize Flask-Admin with custom model views."""
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Star Wars Admin', template_mode='bootstrap3')
    # Restrict admin to users with ADMIN_TOKEN env var (simple example)
    from flask import request, abort
    class SecureModelView(UserView):
        def is_accessible(self):
            admin_token = os.environ.get('ADMIN_TOKEN')
            req_token = request.headers.get('X-Admin-Token')
            return admin_token and req_token == admin_token
        def inaccessible_callback(self, name, **kwargs):
            abort(403)
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(PeopleView(People, db.session))
    admin.add_view(PlanetView(Planet, db.session))
    admin.add_view(VehicleView(Vehicle, db.session))
    admin.add_view(FavoriteView(Favorite, db.session))
