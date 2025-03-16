from app import create_app, db
from app.models import Word

def add_sample_words():
    app = create_app()
    with app.app_context():
        # Clear existing words
        Word.query.delete()
        
        # Add new sample words
        words = [
            {'french': 'bonjour', 'english': 'hello'},
            {'french': 'au revoir', 'english': 'goodbye'},
            {'french': 'merci', 'english': 'thank you'},
            {'french': 'oui', 'english': 'yes'},
            {'french': 'non', 'english': 'no'},
            {'french': 'chat', 'english': 'cat'},
            {'french': 'chien', 'english': 'dog'},
            {'french': 'maison', 'english': 'house'},
            {'french': 'école', 'english': 'school'},
            {'french': 'livre', 'english': 'book'},
            {'french': 'table', 'english': 'table'},
            {'french': 'chaise', 'english': 'chair'},
            {'french': 'fenêtre', 'english': 'window'},
            {'french': 'porte', 'english': 'door'},
            {'french': 'voiture', 'english': 'car'}
        ]
        
        for word_data in words:
            word = Word(**word_data)
            db.session.add(word)
        
        db.session.commit()
        print(f"Added {len(words)} words to the database")

if __name__ == '__main__':
    add_sample_words()
