from app import create_app, db
from app.models import Word, Group, word_group

app = create_app()

with app.app_context():
    # Get the first group
    group = Group.query.get(1)
    
    # Get all words
    words = Word.query.all()[:10]
    
    # Add words to group
    for word in words:
        if group not in word.groups:
            word.groups.append(group)
    
    # Commit changes
    db.session.commit()
    
    # Verify the words were added
    word_count = Word.query.join(Word.groups).filter(Group.id == group.id).count()
    print(f"Added words to group '{group.name}'. Total words in group: {word_count}")
