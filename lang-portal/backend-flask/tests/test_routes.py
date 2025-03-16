import unittest
from app import create_app, db
from app.models import Word, Group, StudySession, StudyActivity, WordReviewItem
from datetime import datetime, timedelta

class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and create new database for testing."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Reset database
        db.drop_all()
        db.create_all()
        
        # Create test data
        self.create_test_data()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_data(self):
        """Create test data for the test cases."""
        # Create study activities
        activities = [
            StudyActivity(name='Flashcards'),
            StudyActivity(name='Multiple Choice'),
            StudyActivity(name='Writing Practice')
        ]
        for activity in activities:
            db.session.add(activity)

        # Create a test group
        group = Group(name='Test Group')
        db.session.add(group)

        # Create test words
        words = [
            Word(english='hello', french='bonjour'),
            Word(english='goodbye', french='au revoir')
        ]
        for word in words:
            db.session.add(word)
            group.words.append(word)

        db.session.commit()

        # Create a study session
        session = StudySession(
            group_id=group.id,
            study_activity_id=activities[0].id,
            created_at=datetime.utcnow()
        )
        db.session.add(session)

        # Add word reviews
        for word in words:
            review = WordReviewItem(
                word_id=word.id,
                study_session_id=session.id,
                is_correct=True
            )
            db.session.add(review)

        db.session.commit()

        self.test_group_id = group.id
        self.test_activity_id = activities[0].id
        self.test_session_id = session.id
        self.test_word_ids = [w.id for w in words]

    def test_get_study_activities(self):
        """Test getting all study activities."""
        response = self.client.get('/api/study_activities')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'Flashcards')

    def test_get_study_activity(self):
        """Test getting a specific study activity."""
        response = self.client.get(f'/api/study_activities/{self.test_activity_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Flashcards')
        self.assertTrue('description' in data)

    def test_get_last_study_session(self):
        """Test getting the last study session."""
        response = self.client.get('/api/dashboard/last_study_session')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['has_sessions'])
        self.assertEqual(data['stats']['total_words'], 2)
        self.assertEqual(data['stats']['correct_words'], 2)

    def test_get_dashboard_quick_stats(self):
        """Test getting dashboard quick stats."""
        response = self.client.get('/api/dashboard/quick_stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total_groups'], 1)
        self.assertEqual(data['total_words'], 2)
        self.assertEqual(data['study_sessions'], 1)
        self.assertTrue('study_streak' in data)
        self.assertTrue('words_studied' in data)

    def test_get_words(self):
        """Test getting all words."""
        response = self.client.get('/api/words')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['words']), 2)
        self.assertEqual(data['total'], 2)
        self.assertEqual(data['words'][0]['english'], 'hello')

    def test_get_groups(self):
        """Test getting all groups."""
        response = self.client.get('/api/groups')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['groups']), 1)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['groups'][0]['name'], 'Test Group')

    def test_get_group_words(self):
        """Test getting words for a specific group."""
        response = self.client.get(f'/api/groups/{self.test_group_id}/words')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['words']), 2)
        self.assertEqual(data['total'], 2)

    def test_get_group_study_sessions(self):
        """Test getting study sessions for a specific group."""
        response = self.client.get(f'/api/groups/{self.test_group_id}/study_sessions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['sessions']), 1)

    def test_get_session_words(self):
        """Test getting words reviewed in a study session."""
        response = self.client.get(f'/api/study_sessions/{self.test_session_id}/words')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['words']), 2)
        self.assertTrue(all(w['is_correct'] for w in data['words']))

if __name__ == '__main__':
    unittest.main()
