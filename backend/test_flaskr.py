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
        self.username = 'postgres'
        self.password = 'pass'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.username,self.password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        self.new_question = {
            'question': 'This is a test',
            'answer': 'tasty test',
            'category': 6,
            'difficulty': 3    
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
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))

    def test_invalid_get_categories(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], "Method not allowed")


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], "")
        self.assertTrue(len(data['categories']))

    def test_invalid_get_question(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions_by_category(self):
        
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        # print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'], 4)
        self.assertEqual(data['current_category'], 2)

    def test_questions_by_category_not_found(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Not found")
    
    def test_delete_questions(self):
        res = self.client().delete('/questions/20')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 20).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_questions_not_found(self):
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 999).first()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable") 

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        

    def test_add_invalid_question(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Unprocessable")

    def test_play_quizzes(self):
        res = self.client().post('/quizzes', json={"previous_questions":[],"quiz_category":{"type":"click","id":0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['question']))

    def test_invalid_play_quizzes(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], "Method not allowed")

    def test_search(self):
        res = self.client().post('questions/search', json={"searchTerm":"Auto"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))


    def test_invalid_search(self):
        res = self.client().post('questions/search', json={"searchTerm":"Thistermdoesntexist.exe"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "Not found")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()