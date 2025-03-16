from app import create_app
from app.models import Group, db

def check_and_create_groups():
    app = create_app()
    with app.app_context():
        # Check existing groups
        groups = Group.query.all()
        print(f"Found {len(groups)} existing groups:")
        for group in groups:
            print(f"- ID: {group.id}, Name: {group.name}")
        
        # If no groups exist, create some sample groups
        if len(groups) == 0:
            print("\nCreating sample word groups...")
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

if __name__ == "__main__":
    check_and_create_groups()
