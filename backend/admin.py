import os
from flask_admin import Admin
from models import db, User, People, Planet, Vehicle, Favorite
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from wtforms import PasswordField
from wtforms.validators import DataRequired

class UserView(ModelView):
    """Custom ModelView for User model with proper password handling"""
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    
    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.password = PasswordField('Password', [DataRequired()])
        return form_class
    
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

class ImageModelView(ModelView):
    """Custom ModelView for models with image URLs"""
    def _list_thumbnail(view, context, model, name):
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
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Star Wars Admin', template_mode='bootstrap3')
    
    # Add model views with image support
    admin.add_view(UserView(User, db.session))
    admin.add_view(PeopleView(People, db.session))
    admin.add_view(PlanetView(Planet, db.session))
    admin.add_view(VehicleView(Vehicle, db.session))
    admin.add_view(FavoriteView(Favorite, db.session))
