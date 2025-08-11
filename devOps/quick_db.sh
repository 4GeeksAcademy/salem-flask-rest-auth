#!/bin/bash

# Star Wars Database Management Script
# Complete database operations and quick actions for the Flask REST API

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m' 
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/../backend"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check if we're in a pipenv environment
check_pipenv() {
    cd "$BACKEND_DIR"
    if [ ! -f "Pipfile" ]; then
        print_error "Pipfile not found in backend directory"
        print_status "Please ensure you're running this from the project root and backend/Pipfile exists"
        exit 1
    fi
}

# Database migration functions
init_db() {
    print_header "Initializing Database"
    cd "$BACKEND_DIR"
    
    print_status "Initializing Alembic migrations..."
    FLASK_APP=app.py pipenv run flask db init 2>/dev/null || print_warning "Migration folder already exists"
    
    print_status "Creating initial migration..."
    FLASK_APP=app.py pipenv run flask db migrate -m "Initial migration"
    
    print_status "Applying migrations..."
    FLASK_APP=app.py pipenv run flask db upgrade
    
    print_success "Database initialized successfully!"
}

migrate_db() {
    print_header "Creating New Migration"
    cd "$BACKEND_DIR"
    
    local message="${1:-Auto migration}"
    print_status "Creating migration: $message"
    FLASK_APP=app.py pipenv run flask db migrate -m "$message"
    
    print_success "Migration created successfully!"
    print_status "Don't forget to run: $0 upgrade"
}

upgrade_db() {
    print_header "Upgrading Database"
    cd "$BACKEND_DIR"
    
    print_status "Applying pending migrations..."
    FLASK_APP=app.py pipenv run flask db upgrade
    
    print_success "Database upgraded successfully!"
}

downgrade_db() {
    print_header "Downgrading Database"
    cd "$BACKEND_DIR"
    
    local revision="${1:--1}"
    print_warning "Downgrading database to revision: $revision"
    FLASK_APP=app.py pipenv run flask db downgrade "$revision"
    
    print_success "Database downgraded successfully!"
}

show_history() {
    print_header "Migration History"
    cd "$BACKEND_DIR"
    
    FLASK_APP=app.py pipenv run flask db history
}

show_current() {
    print_header "Current Migration"
    cd "$BACKEND_DIR"
    
    FLASK_APP=app.py pipenv run flask db current
}

# Data management functions
add_sample_data() {
    print_header "Adding Sample Star Wars Data"
    cd "$BACKEND_DIR"
    
    print_status "Running add_data.py script..."
    pipenv run python add_data.py
    
    print_success "Sample data added successfully!"
}

create_users() {
    print_header "Creating Sample Users"
    cd "$BACKEND_DIR"
    
    cat > bulk_users.py << 'EOF'
#!/usr/bin/env python3

from app import create_app
from models import db, User

def create_sample_users():
    """Create sample users for testing"""
    
    app = create_app()
    with app.app_context():
        
        sample_users = [
            {"email": "luke@jedi.com", "password": "usetheforce"},
            {"email": "leia@rebellion.com", "password": "rebel123"},
            {"email": "han@smuggler.com", "password": "falcon123"},
            {"email": "vader@empire.com", "password": "darkside"},
            {"email": "obi-wan@jedi.com", "password": "highground"},
            {"email": "yoda@jedi.com", "password": "master900"},
            {"email": "admin@starwars.com", "password": "admin123"},
            {"email": "test@example.com", "password": "test123"}
        ]
        
        print("Creating sample users...")
        created_count = 0
        
        for user_data in sample_users:
            # Check if user already exists
            existing = User.query.filter_by(email=user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    is_active=True
                )
                user.set_password(user_data["password"])  # Use bcrypt hashing
                db.session.add(user)
                created_count += 1
                print(f"✅ Created user: {user_data['email']}")
            else:
                user = existing
                print(f"⚠️  User {user_data['email']} already exists")

            # Always ensure admin@starwars.com has the 'admin' role
            if user.email == "admin@starwars.com":
                from models import Role
                admin_role = Role.query.filter_by(name="admin").first()
                if not admin_role:
                    admin_role = Role(name="admin")
                    db.session.add(admin_role)
                    db.session.commit()
                if admin_role not in user.roles:
                    user.roles.append(admin_role)
                    print("🔑 Assigned 'admin' role to admin@starwars.com")
        
        try:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} new users!")
            
            total_users = User.query.count()
            print(f"👥 Total users in database: {total_users}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating users: {e}")

if __name__ == "__main__":
    create_sample_users()
EOF
    
    print_status "Creating sample users..."
    pipenv run python bulk_users.py
    
    # Clean up temporary script
    rm bulk_users.py
    
    print_success "Sample users created successfully!"
}

remove_users() {
    print_header "Removing Users"
    cd "$BACKEND_DIR"
    
    local pattern="${1}"
    
    if [ -z "$pattern" ]; then
        print_error "Please provide an email pattern to remove users"
        print_status "Usage: $0 remove-users <email_pattern>"
        print_status "Example: $0 remove-users 'test@%' (removes all emails starting with test@)"
        return 1
    fi
    
    cat > remove_users.py << EOF
#!/usr/bin/env python3

from app import create_app
from models import db, User, Favorite

def remove_users_by_pattern(pattern):
    """Remove users matching email pattern"""
    
    app = create_app()
    with app.app_context():
        
        # Find users matching pattern
        if '%' in pattern:
            users = User.query.filter(User.email.like('$pattern')).all()
        else:
            users = User.query.filter(User.email == '$pattern').all()
        
        if not users:
            print(f"⚠️  No users found matching pattern: $pattern")
            return
        
        print(f"Found {len(users)} users matching pattern: $pattern")
        for user in users:
            print(f"  - {user.email}")
        
        # Confirm deletion
        confirm = input(f"\\nAre you sure you want to delete these {len(users)} users? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y']:
            try:
                # Delete users (favorites will be cascade deleted)
                for user in users:
                    print(f"🗑️  Deleting user: {user.email}")
                    db.session.delete(user)
                
                db.session.commit()
                print(f"\\n✅ Successfully deleted {len(users)} users!")
                
                remaining_users = User.query.count()
                print(f"👥 Remaining users in database: {remaining_users}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error deleting users: {e}")
        else:
            print("❌ User deletion cancelled")

if __name__ == "__main__":
    remove_users_by_pattern('$pattern')
EOF
    
    pipenv run python remove_users.py
    
    # Clean up temporary script
    rm remove_users.py
}

list_users() {
    print_header "Database Users"
    cd "$BACKEND_DIR"
    
    cat > list_users.py << 'EOF'
#!/usr/bin/env python3

from app import create_app
from models import db, User, Favorite

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
            print(f"ID: {user.id:3} | Email: {user.email:25} | Status: {status:8} | Favorites: {favorites_count}")

if __name__ == "__main__":
    list_all_users()
EOF
    
    pipenv run python list_users.py
    
    # Clean up temporary script
    rm list_users.py
}

reset_db() {
    print_header "Resetting Database"
    
    print_warning "This will completely reset your database and lose all data!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_status "Database reset cancelled"
        return
    fi
    
    cd "$BACKEND_DIR"
    
    print_status "Removing database file..."
    rm -f ../instance/database.db
    
    print_status "Dropping migrations..."
    rm -rf ../migrations/versions/*
    
    print_status "Reinitializing database..."
    init_db
    
    print_success "Database reset complete!"
}

backup_db() {
    print_header "Backing Up Database"
    
    local backup_name="backup_$(date +%Y%m%d_%H%M%S).db"
    local backup_path="$SCRIPT_DIR/backups/$backup_name"
    
    mkdir -p "$SCRIPT_DIR/backups"
    
    print_status "Creating backup: $backup_name"
    cp "$SCRIPT_DIR/../instance/database.db" "$backup_path"
    
    print_success "Database backed up to: $backup_path"
}

# Quick menu for common operations
show_quick_menu() {
    echo -e "${CYAN}🌟 Star Wars Database Quick Actions${NC}"
    echo "=================================="
    echo ""
    echo -e "${YELLOW}Quick Actions:${NC}"
    echo "1. Add Star Wars data     - $0 1"
    echo "2. Create sample users    - $0 2" 
    echo "3. List users            - $0 3"
    echo "4. Backup database       - $0 4"
    echo "5. Reset database        - $0 5"
    echo ""
    echo -e "${YELLOW}Advanced Commands:${NC}"
    echo "  init                    Initialize database and migrations"
    echo "  migrate [message]       Create new migration"
    echo "  upgrade                 Apply pending migrations"
    echo "  downgrade [revision]    Downgrade to revision"
    echo "  history                 Show migration history"
    echo "  current                 Show current migration"
    echo "  remove-users <pattern>  Remove users matching email pattern"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 migrate 'Add new table'"
    echo "  $0 remove-users 'test@%'"
}

# Help function
show_help() {
    echo -e "${CYAN}Star Wars Database Management Script${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Database Migration Commands:${NC}"
    echo "  init                    Initialize database and migrations"
    echo "  migrate [message]       Create new migration (optional message)"
    echo "  upgrade                 Apply pending migrations"
    echo "  downgrade [revision]    Downgrade to revision (default: -1)"
    echo "  history                 Show migration history"
    echo "  current                 Show current migration"
    echo ""
    echo -e "${YELLOW}Data Management Commands:${NC}"
    echo "  add-data               Add sample Star Wars data"
    echo "  create-users           Create sample users for testing"
    echo "  remove-users <pattern> Remove users matching email pattern"
    echo "  list-users             List all users in database"
    echo ""
    echo -e "${YELLOW}Database Utilities:${NC}"
    echo "  reset                  Reset database completely (WARNING: destroys all data)"
    echo "  backup                 Create database backup"
    echo ""
    echo -e "${YELLOW}Quick Number Commands:${NC}"
    echo "  1                      Add Star Wars data"
    echo "  2                      Create sample users"
    echo "  3                      List users"
    echo "  4                      Backup database"
    echo "  5                      Reset database"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 init"
    echo "  $0 migrate 'Add new table'"
    echo "  $0 upgrade"
    echo "  $0 add-data"
    echo "  $0 create-users"
    echo "  $0 remove-users 'test@%'"
    echo "  $0 list-users"
    echo "  $0 backup"
}

# Main script logic
main() {
    check_pipenv
    
    case "${1:-menu}" in
        # Quick number commands
        "1"|"add-data")
            add_sample_data
            ;;
        "2"|"create-users")
            create_users
            ;;
        "3"|"list-users")
            list_users
            ;;
        "4"|"backup")
            backup_db
            ;;
        "5"|"reset")
            reset_db
            ;;
        # Advanced commands
        "init")
            init_db
            ;;
        "migrate")
            migrate_db "$2"
            ;;
        "upgrade")
            upgrade_db
            ;;
        "downgrade")
            downgrade_db "$2"
            ;;
        "history")
            show_history
            ;;
        "current")
            show_current
            ;;
        "remove-users")
            remove_users "$2"
            ;;
        "help")
            show_help
            ;;
        "menu"|*)
            show_quick_menu
            ;;
    esac
}

# Run main function with all arguments
main "$@"
