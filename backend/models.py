import secrets

import bcrypt
from flask_security.core import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

# Association table for roles and users
roles_users = Table(
    "roles_users",
    db.Model.metadata,
    db.Column("user_id", Integer(), ForeignKey("user.id")),
    db.Column("role_id", Integer(), ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    id = db.Column(Integer(), primary_key=True)
    name = db.Column(String(80), unique=True)
    description = db.Column(String(255))


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    fs_uniquifier: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(32),
    )
    favorites = relationship(
        "Favorite", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    # Flask-Security roles
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=roles_users, backref="users"
    )

    def set_password(self, password):
        """Hash and set password"""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def check_password(self, password):
        """Check if provided password matches the hashed password"""
        password_bytes = password.encode("utf-8")
        hashed_password_bytes = self.password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    def serialize(self):
        # Context7 best practice: include id, email, is_active, roles, and fs_uniquifier for API profile
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "roles": [role.name for role in self.roles],
            "fs_uniquifier": self.fs_uniquifier,
        }

    def get_security_payload(self):
        # For Flask-Security API responses (Context7 best practice)
        rv = {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "roles": [role.name for role in self.roles],
            "fs_uniquifier": self.fs_uniquifier,
        }
        # Add extra fields if needed (e.g., confirmation_needed)
        # rv["confirmation_needed"] = self.confirmed_at is None  # Uncomment if you add confirmed_at
        return rv


class People(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    gender: Mapped[str] = mapped_column(String(20))
    birth_year: Mapped[str] = mapped_column(String(20))
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "image_url": self.image_url,
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(120))
    population: Mapped[str] = mapped_column(String(120))
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "image_url": self.image_url,
        }


class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    model: Mapped[str] = mapped_column(String(120))
    manufacturer: Mapped[str] = mapped_column(String(120))
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "image_url": self.image_url,
        }


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    people_id: Mapped[int] = mapped_column(db.ForeignKey("people.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(db.ForeignKey("planet.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(db.ForeignKey("vehicle.id"), nullable=True)

    people = db.relationship("People")
    planet = db.relationship("Planet")
    vehicle = db.relationship("Vehicle")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people": self.people.serialize() if self.people else None,
            "planet": self.planet.serialize() if self.planet else None,
            "vehicle": self.vehicle.serialize() if self.vehicle else None,
        }
