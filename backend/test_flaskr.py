import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'ahmed', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.created_question = {
            'question': 'What is that?',
            'answer': 'Nothing',
            'difficulty': 4,
            'category': 1
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        resp = self.client().get('/categories')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        resp = self.client().get('/questions')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'] > 0)
        self.assertTrue(data['categories'])

    def test_not_found_page(self):
        resp = self.client().get('/questions?page=5000')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_not_found_category(self):
        resp = self.client().get('/categories/5000/questions')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_category_questions(self):
        resp = self.client().get('/categories/5/questions')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], 5)

    def test_delete_question(self):
        new_question = Question(question = 'What is that?', answer = 'Nothing', difficulty = 5, category = 1)
        new_question.insert()
        id = new_question.id

        total_questions = len(Question.query.all())
        resp = self.client().delete(f'/questions/{id}')
        data = json.loads(resp.data)
        new_total_questions = len(Question.query.all())

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['deleted'], id)
        self.assertEqual(new_total_questions, total_questions - 1)

    def test_delete_not_existing_question(self):
        resp = self.client().delete('/questions/5000')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_not_found_question_to_delete(self):
        resp = self.client().delete('/questions/5000')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        total_questions = len(Question.query.all())
        resp = self.client().post('/questions', json = self.created_question)
        data = json.loads(resp.data)
        new_total_questions = len(Question.query.all())

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(new_total_questions, total_questions + 1)

    def test_create_question_without_answer(self):
        new_question = {
            'question': 'What is that?',
            'answer': '',
            'difficulty': 4,
            'category': 1
        }
        resp = self.client().post('/questions', json = new_question)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable request')

    def test_search_questions(self):
        search_term = {'searchTerm': 'Who'}
        resp = self.client().post('/search', json = search_term)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'] > 0)

    def test_quizzes(self):
        quiz = {'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': 1}}

        resp = self.client().post('/quizzes', json = quiz)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
