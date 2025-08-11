#!/usr/bin/env python3
"""
DB Utility Script for Star Wars Flask REST API (Python version)
Usage: python3 quick_db.py <command> [options]
Commands: init | migrate [msg] | upgrade | downgrade [rev] | history | current | add-data | create-users | remove-users <pattern> | list-users | backup | reset | check-password <email> <password> | test-api
"""
import os
import sys
import subprocess
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent / "backend"
DB_PATH = BACKEND_DIR / "instance/database.db"
MIGRATIONS_DIR = BACKEND_DIR.parent / "migrations/versions"
PIPENV = ["pipenv", "run"]

os.chdir(BACKEND_DIR)

def run_flask(*args):
    return subprocess.run([*PIPENV, "flask", *args], check=True)

def run_python(code):
    return subprocess.run([*PIPENV, "python", "-c", code], check=True)

def init_db():
    """Initialize database with migrations"""
    try:
        run_flask("db", "init")
    except Exception:
        pass
    run_flask("db", "migrate", "-m", "Initial migration")
    run_flask("db", "upgrade")
    print("✅ Database initialized successfully.")

def migrate_db(msg="Auto migration"):
    """Create a new migration"""
    run_flask("db", "migrate", "-m", msg)
    print(f"✅ Migration '{msg}' created. Run 'python3 quick_db.py upgrade' to apply.")

def upgrade_db():
    """Apply pending migrations"""
    run_flask("db", "upgrade")
    print("✅ Database upgraded successfully.")

def downgrade_db(rev="-1"):
    """Downgrade database to a specific revision"""
    run_flask("db", "downgrade", rev)
    print(f"✅ Database downgraded to {rev}.")

def show_history():
    """Show migration history"""
    run_flask("db", "history")

def show_current():
    """Show current migration"""
    run_flask("db", "current")

def add_sample_data():
    """Add comprehensive sample data with enhanced fields"""
    code = '''
from app import create_app
from models import db, People, Planet, Vehicle
from datetime import datetime

app = create_app()
with app.app_context():
    # Check if data already exists
    if People.query.first():
        print("Sample data already exists. Skipping...")
        exit()
    
    # Enhanced People data
    people_data = [
        {
            "name": "Luke Skywalker", 
            "gender": "male", 
            "birth_year": "19BBY", 
            "image_url": "https://starwars-visualguide.com/assets/img/characters/1.jpg"
        },
        {
            "name": "Leia Organa", 
            "gender": "female", 
            "birth_year": "19BBY", 
            "image_url": "https://starwars-visualguide.com/assets/img/characters/5.jpg"
        },
        {
            "name": "Darth Vader", 
            "gender": "male", 
            "birth_year": "41.9BBY", 
            "image_url": "https://starwars-visualguide.com/assets/img/characters/4.jpg"
        },
        {
            "name": "Obi-Wan Kenobi", 
            "gender": "male", 
            "birth_year": "57BBY", 
            "image_url": "https://starwars-visualguide.com/assets/img/characters/10.jpg"
        }
    ]
    
    # Enhanced Planet data
    planets_data = [
        {
            "name": "Tatooine", 
            "climate": "arid", 
            "population": "200000", 
            "image_url": "https://starwars-visualguide.com/assets/img/planets/1.jpg"
        },
        {
            "name": "Alderaan", 
            "climate": "temperate", 
            "population": "2000000000", 
            "image_url": "https://starwars-visualguide.com/assets/img/planets/2.jpg"
        },
        {
            "name": "Coruscant", 
            "climate": "temperate", 
            "population": "1000000000000", 
            "image_url": "https://starwars-visualguide.com/assets/img/planets/9.jpg"
        },
        {
            "name": "Hoth", 
            "climate": "frozen", 
            "population": "unknown", 
            "image_url": "https://starwars-visualguide.com/assets/img/planets/4.jpg"
        }
    ]
    
    # Enhanced Vehicle data
    vehicles_data = [
        {
            "name": "X-wing", 
            "model": "T-65 X-wing starfighter", 
            "manufacturer": "Incom Corporation", 
            "image_url": "https://starwars-visualguide.com/assets/img/vehicles/12.jpg"
        },
        {
            "name": "TIE Fighter", 
            "model": "Twin Ion Engine/Ln starfighter", 
            "manufacturer": "Sienar Fleet Systems", 
            "image_url": "https://starwars-visualguide.com/assets/img/vehicles/13.jpg"
        },
        {
            "name": "Millennium Falcon", 
            "model": "YT-1300 light freighter", 
            "manufacturer": "Corellian Engineering Corporation", 
            "image_url": "https://starwars-visualguide.com/assets/img/vehicles/10.jpg"
        },
        {
            "name": "Imperial Star Destroyer", 
            "model": "Imperial I-class Star Destroyer", 
            "manufacturer": "Kuat Drive Yards", 
            "image_url": "https://starwars-visualguide.com/assets/img/vehicles/3.jpg"
        }
    ]
    
    # Add people
    for person_data in people_data:
        person = People(**person_data)
        db.session.add(person)
    
    # Add planets
    for planet_data in planets_data:
        planet = Planet(**planet_data)
        db.session.add(planet)
    
    # Add vehicles
    for vehicle_data in vehicles_data:
        vehicle = Vehicle(**vehicle_data)
        db.session.add(vehicle)
    
    db.session.commit()
    print(f"✅ Sample data added successfully:")
    print(f"   - {len(people_data)} characters")
    print(f"   - {len(planets_data)} planets") 
    print(f"   - {len(vehicles_data)} vehicles")
'''
    run_python(code)

def create_users():
    """Create sample users with proper role assignment"""
    code = '''
from app import create_app
from models import db, User, Role
import secrets

app = create_app()
with app.app_context():
    # Sample users with varied roles
    sample_users = [
        {
            "email": "admin@starwars.com", 
            "password": "admin123",
            "roles": ["admin"]
        },
        {
            "email": "jedi@starwars.com", 
            "password": "jedimaster",
            "roles": ["user"]
        },
        {
            "email": "1@1.com", 
            "password": "1234567890",
            "roles": ["user"]
        },
        {
            "email": "test@example.com", 
            "password": "password123",
            "roles": ["user"]
        }
    ]
    
    # Ensure required roles exist
    required_roles = ["admin", "user"]
    for role_name in required_roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name.title()} role")
            db.session.add(role)
    
    db.session.commit()
    
    created_count = 0
    updated_count = 0
    
    for user_data in sample_users:
        existing = User.query.filter_by(email=user_data["email"]).first()
        
        if not existing:
            # Create new user
            user = User(
                email=user_data["email"], 
                active=True,
                fs_uniquifier=secrets.token_urlsafe(32)
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Assign roles
            for role_name in user_data["roles"]:
                role = Role.query.filter_by(name=role_name).first()
                if role and role not in user.roles:
                    user.roles.append(role)
            
            created_count += 1
        else:
            # Update existing user roles if needed
            for role_name in user_data["roles"]:
                role = Role.query.filter_by(name=role_name).first()
                if role and role not in existing.roles:
                    existing.roles.append(role)
                    updated_count += 1
    
    db.session.commit()
    print(f"✅ User management completed:")
    print(f"   - {created_count} new users created")
    print(f"   - {updated_count} users updated with roles")
    
    # List all users for verification
    users = User.query.all()
    print("\\n📋 Current users:")
    for user in users:
        roles_str = ", ".join([role.name for role in user.roles]) or "no roles"
        print(f"   - {user.email} ({roles_str})")
'''
    run_python(code)

def remove_users(pattern):
    """Remove users matching a pattern"""
    code = f'''
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    if '%' in "{pattern}":
        users = User.query.filter(User.email.like("{pattern}")).all()
    else:
        users = User.query.filter(User.email == "{pattern}").all()
    
    if users:
        user_emails = [user.email for user in users]
        for user in users:
            db.session.delete(user)
        db.session.commit()
        print(f"✅ Deleted {{len(users)}} users:")
        for email in user_emails:
            print(f"   - {{email}}")
    else:
        print("❌ No users found matching pattern: {pattern}")
'''
    run_python(code)

def list_users():
    """List all users with their roles and stats"""
    code = '''
from app import create_app
from models import db, User, Favorite

app = create_app()
with app.app_context():
    users = User.query.all()
    if not users:
        print("❌ No users found in database.")
        return
    
    print(f"📋 Found {len(users)} users:")
    print("-" * 80)
    
    for user in users:
        roles_str = ", ".join([role.name for role in user.roles]) or "no roles"
        favorites_count = len(user.favorites)
        status = "active" if user.active else "inactive"
        
        print(f"ID: {user.id:2d} | {user.email:25s} | {roles_str:15s} | {status:8s} | {favorites_count} favorites")
'''
    run_python(code)

def reset_db():
    """Completely reset database and migrations"""
    print("⚠️  This will completely reset your database and all data will be lost!")
    confirm = input("Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("❌ Reset cancelled.")
        return
    
    # Remove database file
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("🗑️  Removed database file.")
    
    # Remove migrations directory completely
    migrations_root = BACKEND_DIR / "migrations"
    if migrations_root.exists():
        import shutil
        shutil.rmtree(migrations_root)
        print("🗑️  Removed migrations directory.")
    
    # Recreate everything
    init_db()
    print("✅ Database and migrations fully reset.")

def backup_db():
    """Create a timestamped backup of the database"""
    from datetime import datetime
    backup_dir = Path(__file__).parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"starwars_backup_{timestamp}.db"
    backup_path = backup_dir / backup_name
    
    src = BACKEND_DIR / "instance/database.db"
    if src.exists():
        backup_path.write_bytes(src.read_bytes())
        print(f"✅ Database backed up to: {backup_path}")
        print(f"📊 Backup size: {backup_path.stat().st_size} bytes")
    else:
        print("❌ Database file not found.")

def check_user_password(email, password):
    """Debug tool to check user password and authentication"""
    code = f'''
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    print("🔍 Database Connection Info:")
    print(f"   DB URL: {{db.engine.url}}")
    print(f"   DB File exists: {{Path(db.engine.url.database).exists() if db.engine.url.database else False}}")
    
    print("\\n👥 All users in database:")
    all_users = User.query.all()
    if not all_users:
        print("   No users found!")
    else:
        for u in all_users:
            print(f"   - {{u.email}} (ID: {{u.id}}, Active: {{u.active}})")
    
    print(f"\\n🔐 Password Check for: {{repr('{email}')}}")
    user = User.query.filter_by(email="{email}").first()
    
    if not user:
        print("❌ User not found.")
    else:
        print(f"✅ User found: {{user.email}}")
        print(f"   Active: {{user.active}}")
        print(f"   Roles: {{[r.name for r in user.roles]}}")
        print(f"   Hash (first 20 chars): {{user.password[:20]}}...")
        
        try:
            if user.check_password("{password}"):
                print("✅ Password is valid!")
            else:
                print("❌ Invalid password!")
        except Exception as e:
            print(f"💥 Error during password check: {{e}}")
            import traceback
            traceback.print_exc()
'''
    run_python(code)

def test_api_connectivity():
    """Test API endpoints to ensure everything is working"""
    code = '''
from app import create_app
from models import db, User, People, Planet, Vehicle
import json

app = create_app()
with app.app_context():
    print("🧪 API Connectivity Test")
    print("=" * 50)
    
    # Test database connectivity
    try:
        db.session.execute("SELECT 1")
        print("✅ Database connection: OK")
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return
    
    # Count records
    people_count = People.query.count()
    planets_count = Planet.query.count()
    vehicles_count = Vehicle.query.count()
    users_count = User.query.count()
    
    print(f"📊 Data Summary:")
    print(f"   - People: {people_count}")
    print(f"   - Planets: {planets_count}")
    print(f"   - Vehicles: {vehicles_count}")
    print(f"   - Users: {users_count}")
    
    # Test serialization
    if people_count > 0:
        person = People.query.first()
        try:
            serialized = person.serialize()
            print("✅ People serialization: OK")
        except Exception as e:
            print(f"❌ People serialization: FAILED - {e}")
    
    print("\\n🚀 Ready for API testing!")
    print("   Try: curl http://localhost:3000/api/people")
'''
    run_python(code)

def show_help():
    """Display help information"""
    print("""
🚀 Star Wars Flask API - Database Management Tool
=" * 60)

Usage: python3 quick_db.py <command> [options]

📋 Available Commands:
   init                     Initialize database and migrations
   migrate [message]        Create a new migration (default: "Auto migration")
   upgrade                  Apply pending migrations
   downgrade [revision]     Downgrade to specific revision (default: -1)
   history                  Show migration history
   current                  Show current migration
   
   add-data                 Add sample Star Wars data
   create-users             Create sample users with roles
   list-users               List all users with details
   remove-users <pattern>   Remove users (supports % wildcards)
   check-password <email> <password>  Debug password authentication
   
   backup                   Create timestamped database backup
   reset                    DANGER: Completely reset database (asks for confirmation)
   test-api                 Test API connectivity and data integrity

🔢 Shortcuts:
   1 = add-data    2 = create-users    3 = list-users    4 = backup    5 = reset

💡 Examples:
   python3 quick_db.py init
   python3 quick_db.py add-data
   python3 quick_db.py create-users
   python3 quick_db.py check-password admin@starwars.com admin123
   python3 quick_db.py remove-users "%test%"
""")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    cmd = sys.argv[1]
    
    # Command routing with shortcuts
    if cmd in ("add-data", "1"): 
        add_sample_data()
    elif cmd in ("create-users", "2"): 
        create_users()
    elif cmd in ("list-users", "3"): 
        list_users()
    elif cmd in ("backup", "4"): 
        backup_db()
    elif cmd in ("reset", "5"): 
        reset_db()
    elif cmd == "init": 
        init_db()
    elif cmd == "migrate": 
        migrate_db(sys.argv[2] if len(sys.argv) > 2 else "Auto migration")
    elif cmd == "upgrade": 
        upgrade_db()
    elif cmd == "downgrade": 
        downgrade_db(sys.argv[2] if len(sys.argv) > 2 else "-1")
    elif cmd == "history": 
        show_history()
    elif cmd == "current": 
        show_current()
    elif cmd == "test-api":
        test_api_connectivity()
    elif cmd == "check-password":
        if len(sys.argv) < 4:
            print("Usage: python3 quick_db.py check-password <email> <password>")
            return
        check_user_password(sys.argv[2], sys.argv[3])
    elif cmd == "remove-users":
        if len(sys.argv) < 3:
            print("Usage: python3 quick_db.py remove-users <pattern>")
            return
        remove_users(sys.argv[2])
    else:
        show_help()

if __name__ == "__main__":
    main()