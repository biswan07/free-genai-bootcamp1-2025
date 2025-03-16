from app import create_app
from app.models import Group, db
import requests

def debug_groups():
    # Check database directly
    app = create_app()
    with app.app_context():
        # Check existing groups in database
        groups = Group.query.all()
        print(f"Database check - Found {len(groups)} groups:")
        for group in groups:
            print(f"- ID: {group.id}, Name: {group.name}")
        
        # If no groups exist, create some sample groups
        if len(groups) == 0:
            print("\nNo groups found in database. Creating sample groups...")
            sample_groups = [
                Group(name="Basic Vocabulary"),
                Group(name="Intermediate Words"),
                Group(name="Advanced Terminology")
            ]
            
            db.session.add_all(sample_groups)
            db.session.commit()
            
            print("Created sample groups:")
            for group in sample_groups:
                print(f"- ID: {group.id}, Name: {group.name}")
    
    # Check API response
    try:
        response = requests.get('http://localhost:5000/api/groups')
        print("\nAPI Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
    except Exception as e:
        print(f"Error making API request: {e}")

if __name__ == "__main__":
    debug_groups()
