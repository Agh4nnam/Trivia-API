import os
from flask import Flask, request, abort, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)
  CORS(app) 
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''    
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categorylist= {category.id:category.type for category in categories}

    if len(categories) == 0:
          abort(404)

    return jsonify({
      'success': True,
      'categories': categorylist
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = Question.query.all()
    categories = Category.query.all()
    formatted_questions = [question.format() for question in questions]
    paginated_questions = formatted_questions[start:end]
    categorylist= {category.id:category.type for category in categories}

    # print(categories)
    # print(len(paginated_questions))

    if len(paginated_questions) == 0:
          abort(404)

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(questions),
      'current_category': '', #perhaps not needed?
      'categories': categorylist
    })

  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
        question = Question.query.get(question_id)
        try:
          Question.delete(question)
          return jsonify({
            'success': True
            })
        except:
          abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
        data = request.get_json()
        try:
          question = Question(data['question'],data['answer'],data['category'],data['difficulty'])
          #print("posted question cat " + data['category'])
          Question.insert(question)
          return jsonify({
            'data': data,
            'success': True
            })
        except:
          abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
        searchTerm = request.get_json()['searchTerm']
        questions = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()
        questions = [question.format() for question in questions]
        if len(questions) == 0:
              abort(404)

        return jsonify({
          'success': True,
          'questions': questions,
          'totalQuestions': len(questions),
          'currentCategory': ''
        })
        

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def get_questions_by_category(cat_id):
    questions = Question.query.filter(Question.category == cat_id).all()

    formatted_questions = [question.format() for question in questions]

    if(len(formatted_questions) == 0):
          abort(404)

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(questions),
      'current_category': cat_id,
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play():
        requestJSON = request.get_json()
        category = requestJSON['quiz_category']['id']
        previousQuestions = requestJSON['previous_questions']
        
        if category == 0:
              # print('ALL was chosen!')
              questions = Question.query.filter(Question.id.notin_(previousQuestions)).all()
             

        else:
          questions = Question.query.filter(Question.category == category, Question.id.notin_(previousQuestions)).all()
        

        if len(questions) == 0: #stops the quiz if questions pool is exhausted
          return jsonify({ 
          'question': None,
          })

        question = questions[random.randrange(len(questions))]
        question = question.format()
        #previousQuestions = [question.format() for question in previousQuestions]


        return jsonify({
        'question': question,
        })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found"
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "Method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422


  return app

    