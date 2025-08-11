"""Flask-Admin configuration and custom model views for the Star Wars API backend."""

import os

from flask import flash, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from markupsafe import Markup
from models import Favorite, People, Planet, User, Vehicle, db
from wtforms import PasswordField
from wtforms.validators import DataRequired


class UserView(ModelView):
    """Custom ModelView for User model with proper password handling"""

    column_exclude_list = ["password"]
    form_excluded_columns = ["password"]

    def scaffold_form(self):
        """Customize the form to include a password field."""
        form_class = super().scaffold_form()
        form_class.password = PasswordField("Password", [DataRequired()])
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
            return Markup(
                f'<img src="{model.image_url}" style="max-width: 80px; max-height: 80px;">'
            )
        return ""

    column_formatters = {"image_url": _list_thumbnail}


class PeopleView(ImageModelView):
    column_list = ["name", "gender", "birth_year", "image_url"]
    column_labels = {"image_url": "Image Preview"}
    form_columns = ["name", "gender", "birth_year", "image_url"]


class PlanetView(ImageModelView):
    column_list = ["name", "climate", "population", "image_url"]
    column_labels = {"image_url": "Image Preview"}
    form_columns = ["name", "climate", "population", "image_url"]


class VehicleView(ImageModelView):
    column_list = ["name", "model", "manufacturer", "image_url"]
    column_labels = {"image_url": "Image Preview"}
    form_columns = ["name", "model", "manufacturer", "image_url"]


class FavoriteView(ModelView):
    column_list = ["user.email", "people.name", "planet.name", "vehicle.name"]
    column_labels = {
        "user.email": "User Email",
        "people.name": "Favorite Character",
        "planet.name": "Favorite Planet",
        "vehicle.name": "Favorite Vehicle",
    }


class SecureAdminIndexView(AdminIndexView):
    """Secure admin index view that requires admin role."""
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role("admin")

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for("security.login"))


class SecureModelView(ModelView):
    """Base secure model view that requires admin role."""
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role("admin")

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for("security.login"))


class SecureUserView(UserView, SecureModelView):
    """Secure user view combining UserView functionality with security."""
    pass


class SecurePeopleView(PeopleView, SecureModelView):
    """Secure people view with image preview and admin access control."""
    pass


class SecurePlanetView(PlanetView, SecureModelView):
    """Secure planet view with image preview and admin access control."""
    pass


class SecureVehicleView(VehicleView, SecureModelView):
    """Secure vehicle view with image preview and admin access control."""
    pass


class SecureFavoriteView(FavoriteView, SecureModelView):
    """Secure favorite view with admin access control."""
    pass


def init_admin(app):
    """Initialize Flask-Admin and register with the app."""
    # Don't override the secret key if it's already set
    if not app.secret_key:
        app.secret_key = os.environ.get("FLASK_APP_KEY", "sample key")
    
    # Set Flask-Admin theme
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    # Initialize admin with secure index view
    admin = Admin(
        app,
        name="Star Wars Admin",
        template_mode="bootstrap3",
        index_view=SecureAdminIndexView(),
    )
    
    # Add secure model views
    admin.add_view(SecureUserView(User, db.session, name="Users"))
    admin.add_view(SecurePeopleView(People, db.session, name="Characters"))
    admin.add_view(SecurePlanetView(Planet, db.session, name="Planets"))
    admin.add_view(SecureVehicleView(Vehicle, db.session, name="Vehicles"))
    admin.add_view(SecureFavoriteView(Favorite, db.session, name="Favorites"))
    
    return admin