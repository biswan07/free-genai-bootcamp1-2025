import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Word

# List of French-English word pairs
words = [
    {"french": "bonjour", "english": "hello"},
    {"french": "au revoir", "english": "goodbye"},
    {"french": "merci", "english": "thank you"},
    {"french": "oui", "english": "yes"},
    {"french": "non", "english": "no"},
    {"french": "chat", "english": "cat"},
    {"french": "chien", "english": "dog"},
    {"french": "maison", "english": "house"},
    {"french": "école", "english": "school"},
    {"french": "livre", "english": "book"},
    {"french": "dans", "english": "in"},  # Adding the word "dans"
]

app = create_app()

with app.app_context():
    # Add each word to the database
    for word_data in words:
        word = Word(
            french=word_data["french"],
            english=word_data["english"]
        )
        db.session.add(word)
    
    # Commit the changes
    db.session.commit()
    print("Initial words added successfully!")
