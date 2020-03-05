import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgres://laura@localhost:5432/trivia_test"
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'The Answer to the Ultimate Question of Life, the Universe, and Everything',
            'answer': '42',
            'category': 1,
            'difficulty': 100
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Write at least one test for each test for successful operation and for expected errors.

    # '/categories', methods=['GET']

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    # '/questions', methods=['GET']

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    def test_404_invalid_page_number(self):
        res = self.client().get('/questions/?page=10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # '/question/<int:question_id>', methods=['DELETE']

    def test_delete_question(self):
        new_id = self.client().post('/question', json=self.new_question).json['created']
        res = self.client().delete(f'/question/{new_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_id)

    def test_422_question_does_not_exist(self):
        res = self.client().delete('/question/1500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # '/question', methods=['POST']

    def test_create_new_question(self):
        res = self.client().post('/question', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_405_creation_not_allowed(self):
        res = self.client().post('/question/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    # '/questions/search', methods=['POST']
    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'blab'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_search_term_not_available(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'XYZTRWQSD'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # '/category/<int:category_id>/questions', methods=['GET']
    def test_get_questions_of_category(self):
        res = self.client().get('/category/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_invalid_category(self):
        res = self.client().get('/category/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # '/quizzes', methods=['POST']
    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': '2'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_200_invalid_category(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': '100'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNone(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
