#!/usr/bin/env python3

from app import create_app
from models import Favorite, User, db


def list_all_users():
    """List all users in the database"""

    app = create_app()
    with app.app_context():

        users = User.query.all()

        if not users:
            print("No users found in database")
            return

        print(f"Found {len(users)} users:")
        print("-" * 60)

        for user in users:
            favorites_count = Favorite.query.filter_by(user_id=user.id).count()
            status = "Active" if user.is_active else "Inactive"
            print(
                f"ID: {user.id:3} | Email: {user.email:25} | Status: {status:8} | Favorites: {favorites_count}"
            )


if __name__ == "__main__":
    list_all_users()
