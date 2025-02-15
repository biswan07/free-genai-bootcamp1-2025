from app import create_app, db
from app.models import Word, Group

def add_words():
    app = create_app()
    with app.app_context():
        # Create a default group
        basic_group = Group.query.filter_by(name='Basic Vocabulary').first()
        if not basic_group:
            basic_group = Group(name='Basic Vocabulary')
            db.session.add(basic_group)
        
        # Common French-English word pairs
        word_pairs = [
            ('bonjour', 'hello'),
            ('au revoir', 'goodbye'),
            ('merci', 'thank you'),
            ('s\'il vous plaît', 'please'),
            ('oui', 'yes'),
            ('non', 'no'),
            ('je', 'I'),
            ('tu', 'you'),
            ('il', 'he'),
            ('elle', 'she'),
            ('nous', 'we'),
            ('vous', 'you (formal/plural)'),
            ('ils', 'they (masculine)'),
            ('elles', 'they (feminine)'),
            ('être', 'to be'),
            ('avoir', 'to have'),
            ('faire', 'to do/make'),
            ('aller', 'to go'),
            ('venir', 'to come'),
            ('voir', 'to see'),
            ('manger', 'to eat'),
            ('boire', 'to drink'),
            ('dormir', 'to sleep'),
            ('parler', 'to speak'),
            ('écouter', 'to listen'),
            ('lire', 'to read'),
            ('écrire', 'to write'),
            ('un', 'one'),
            ('deux', 'two'),
            ('trois', 'three'),
            ('quatre', 'four'),
            ('cinq', 'five'),
            ('maison', 'house'),
            ('chat', 'cat'),
            ('chien', 'dog'),
            ('livre', 'book'),
            ('table', 'table'),
            ('chaise', 'chair'),
            ('porte', 'door'),
            ('fenêtre', 'window'),
            ('eau', 'water'),
            ('pain', 'bread'),
            ('fromage', 'cheese'),
            ('vin', 'wine'),
            ('café', 'coffee'),
            ('thé', 'tea'),
            ('pomme', 'apple'),
            ('orange', 'orange'),
            ('banane', 'banana'),
            ('rouge', 'red')
        ]

        # Add words to database
        for french, english in word_pairs:
            word = Word.query.filter_by(french=french, english=english).first()
            if not word:
                word = Word(french=french, english=english)
                word.groups.append(basic_group)
                db.session.add(word)

        db.session.commit()
        print("Successfully added 50 words to the database!")

if __name__ == '__main__':
    add_words()
