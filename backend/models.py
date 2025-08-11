import secrets
from datetime import datetime
from typing import Optional

import bcrypt
from flask_security.core import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Table
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
    """Role model for Flask-Security role-based access control."""
    
    id = db.Column(Integer(), primary_key=True)
    name = db.Column(String(80), unique=True, nullable=False)
    description = db.Column(String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    """User model with Flask-Security integration."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    fs_uniquifier: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(32),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    favorites = relationship(
        "Favorite", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=roles_users, backref="users"
    )

    def set_password(self, password):
        """Hash and set user password using Flask-Security utilities."""
        from flask_security.utils import hash_password
        self.password = hash_password(password)

    def check_password(self, password):
        """Verify user password using Flask-Security utilities."""
        from flask_security.utils import verify_password
        return verify_password(password, self.password)
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def add_role(self, role_name):
        """Add a role to the user if not already present."""
        if not self.has_role(role_name):
            role = Role.query.filter_by(name=role_name).first()
            if role:
                self.roles.append(role)

    def serialize(self):
        """Serialize user data for API responses."""
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.active,
            "roles": [role.name for role in self.roles],
            "fs_uniquifier": self.fs_uniquifier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "favorites_count": len(self.favorites)
        }

    def get_security_payload(self):
        """Get payload for Flask-Security API responses."""
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.active,
            "roles": [role.name for role in self.roles],
            "fs_uniquifier": self.fs_uniquifier,
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class People(db.Model):
    """Star Wars characters/people model."""
    
    __tablename__ = 'people'  # Explicit table name for clarity
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    birth_year: Mapped[Optional[str]] = mapped_column(String(20))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    def serialize(self):
        """Serialize character data for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "image_url": self.image_url,
        }
    
    def __repr__(self):
        return f'<People {self.name}>'


class Planet(db.Model):
    """Star Wars planets model."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    climate: Mapped[Optional[str]] = mapped_column(String(120))
    population: Mapped[Optional[str]] = mapped_column(String(120))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    def serialize(self):
        """Serialize planet data for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "image_url": self.image_url,
        }
    
    def __repr__(self):
        return f'<Planet {self.name}>'


class Vehicle(db.Model):
    """Star Wars vehicles model."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    model: Mapped[Optional[str]] = mapped_column(String(120))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(120))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    def serialize(self):
        """Serialize vehicle data for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "image_url": self.image_url,
        }
    
    def __repr__(self):
        return f'<Vehicle {self.name}>'


class Favorite(db.Model):
    """User favorites model for linking users to their favorite items."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    people_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("people.id", ondelete="SET NULL"), nullable=True
    )
    planet_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("planet.id", ondelete="SET NULL"), nullable=True
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("vehicle.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    people = db.relationship("People", lazy='joined')
    planet = db.relationship("Planet", lazy='joined')
    vehicle = db.relationship("Vehicle", lazy='joined')
    
    # Add table constraint to ensure at least one favorite type is set
    __table_args__ = (
        db.CheckConstraint(
            'people_id IS NOT NULL OR planet_id IS NOT NULL OR vehicle_id IS NOT NULL',
            name='check_at_least_one_favorite'
        ),
    )

    @property
    def favorite_type(self):
        """Get the type of favorite this record represents."""
        if self.people_id:
            return "people"
        elif self.planet_id:
            return "planet"
        elif self.vehicle_id:
            return "vehicle"
        return None
    
    @property
    def favorite_item(self):
        """Get the actual favorite item object."""
        if self.people:
            return self.people
        elif self.planet:
            return self.planet
        elif self.vehicle:
            return self.vehicle
        return None

    def serialize(self):
        """Serialize favorite data for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "favorite_type": self.favorite_type,
            "people": self.people.serialize() if self.people else None,
            "planet": self.planet.serialize() if self.planet else None,
            "vehicle": self.vehicle.serialize() if self.vehicle else None,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self):
        item_name = "Unknown"
        if self.people:
            item_name = self.people.name
        elif self.planet:
            item_name = self.planet.name
        elif self.vehicle:
            item_name = self.vehicle.name
        return f'<Favorite {self.user_id}:{item_name}>'