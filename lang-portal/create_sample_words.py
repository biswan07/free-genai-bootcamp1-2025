import sys
import os

# Add the backend-flask directory to the Python path
sys.path.insert(0, os.path.abspath('./backend-flask'))

from app import create_app, db
from app.models import Word, Group

def create_sample_words():
    app = create_app()
    with app.app_context():
        # Check existing words
        words = Word.query.all()
        print(f"Found {len(words)} existing words in database:")
        
        # If no words exist, create some sample words
        if len(words) == 0:
            print("\nCreating sample words in database...")
            
            # Get the groups
            groups = Group.query.all()
            if not groups:
                print("No groups found. Please run create_backend_groups.py first.")
                return
            
            # Create sample words
            sample_words = [
                Word(french="bonjour", english="hello"),
                Word(french="au revoir", english="goodbye"),
                Word(french="merci", english="thank you"),
                Word(french="s'il vous plaît", english="please"),
                Word(french="oui", english="yes"),
                Word(french="non", english="no"),
                Word(french="chat", english="cat"),
                Word(french="chien", english="dog"),
                Word(french="maison", english="house"),
                Word(french="voiture", english="car")
            ]
            
            # Add all words to the first group
            first_group = groups[0]
            for word in sample_words:
                word.groups.append(first_group)
            
            db.session.add_all(sample_words)
            db.session.commit()
            
            print(f"Created {len(sample_words)} sample words and added them to group: {first_group.name}")
        else:
            print("Words already exist, no need to create new ones.")

if __name__ == "__main__":
    create_sample_words()
