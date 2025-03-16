import sys
import os

# Add the backend-flask directory to the Python path
sys.path.insert(0, os.path.abspath('./backend-flask'))

from app import create_app, db
from app.models import Group

def create_groups():
    app = create_app()
    with app.app_context():
        # Check existing groups
        groups = Group.query.all()
        print(f"Found {len(groups)} existing groups in backend database:")
        for group in groups:
            print(f"- ID: {group.id}, Name: {group.name}")
        
        # If no groups exist, create some sample groups
        if len(groups) == 0:
            print("\nCreating sample word groups in backend database...")
            sample_groups = [
                Group(name="Basic French Vocabulary"),
                Group(name="Intermediate French"),
                Group(name="Advanced French")
            ]
            
            db.session.add_all(sample_groups)
            db.session.commit()
            
            print("Created sample groups:")
            for group in sample_groups:
                print(f"- ID: {group.id}, Name: {group.name}")
        else:
            print("Groups already exist, no need to create new ones.")

if __name__ == "__main__":
    create_groups()
