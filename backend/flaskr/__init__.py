import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={'/': {'origins': '*'}})
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(resp):
        resp.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
            )
        resp.headers.add(
            'Access-Control-Allow-Headers',
            'GET, POST, PATCH, DELETE, OPTION'
            )
        return resp

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if (len(categories) == 0):
            abort(404)

        return jsonify({
          'success': True,
          'categories': {category.id: category.type for category in categories}
          })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at
    the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()

        if (len(current_questions) == 0):
            abort(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'current category': None,
          'categories': {category.id: category.type for category in categories}
          })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id) \
            .one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({
          'success': True,
          'deleted': question_id,
          })

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        created_question = body.get('question')
        created_answer = body.get('answer')
        created_difficulty = body.get('difficulty')
        created_category = body.get('category')

        if (created_question == '') or (created_answer == ''):
            abort(422)

        question = Question(
          question=created_question,
          answer=created_answer,
          difficulty=created_difficulty,
          category=created_category)

        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(selection)
          })

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)
        try:
            questions_found = Question.query.order_by(Question.id) \
                .filter(Question.question.ilike('%{}%'.format(search)))
            questions = paginate_questions(request, questions_found)

            if (len(questions) == 0):
                abort(422)

            return jsonify({
              'success': True,
              'questions': questions,
              'total_questions': len(questions),
              'current_category': None
              })
        except:
            abort(422)
    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        category = Category.query.filter_by(id=category_id).one_or_none()

        if (category is None):
            abort(404)

        category_questions = Question.query.order_by(Question.id) \
            .filter_by(category=category.id).all()
        questions = paginate_questions(request, category_questions)

        return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': len(questions),
          'current_category': category_id
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

        try:
            body = request.get_json()
            category = body.get('quiz_category', None)
            previous_questions = body.get('previous_questions', None)

            if (category is None):
                abort(404)

            if (category['id'] == 0):
                questions = Question.query \
                    .filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query \
                    .filter(Question.id.notin_(previous_questions)) \
                    .filter_by(category=category['id']).all()

            category_questions_count = len(questions)
            previous_questions_count = len(previous_questions)

            if (category_questions_count <= previous_questions_count):
                return jsonify({
                  'success': True,
                  'question': None
                  })

            random_question = questions[random.randrange(
                0,
                category_questions_count)].format()

            return jsonify({
              'success': True,
              'question': random_question
              })
        except:
            abort(422)
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
          }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable request"
          }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
          }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
          "success": False,
          "error": 500,
          "message": "internal server error"
          }), 500

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
          "success": False,
          "error": 405,
          "message": "method not allowed"
          }), 405

    return app
