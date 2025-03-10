import sqlite3
import os

def upgrade():
    """Add session_data column to study_sessions table."""
    # Get the database path - using the instance folder where Flask stores the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'lang_portal.db')
    
    print(f"Using database path: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(study_sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'session_data' not in columns:
            # Add the column if it doesn't exist
            cursor.execute('ALTER TABLE study_sessions ADD COLUMN session_data JSON NULL')
            print("Added session_data column to study_sessions table")
        else:
            print("session_data column already exists in study_sessions table")
        
        # Commit the changes
        conn.commit()
    except Exception as e:
        print(f"Error adding session_data column: {str(e)}")
        conn.rollback()
    finally:
        # Close the connection
        conn.close()

if __name__ == '__main__':
    upgrade()
