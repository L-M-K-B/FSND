import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# ##--------------------------------------------------## #
# ##--------------------- helpers --------------------## #
# ##--------------------------------------------------## #

QUESTIONS_PER_PAGE = 10


def paginate_questions(selection):
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in selection]
    current_questions = formatted_questions[start:end]

    return current_questions

# ##--------------------------------------------------## #

def create_categories_dict(query_res):
    categories_dict = {}

    for category in query_res:
        categories_dict[category.id] = category.type

    return categories_dict

# ##--------------------------------------------------## #
# ##--------------------------------------------------## #
# ##--------------------------------------------------## #

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app)

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS  ')
        return response

    # Create an endpoint to handle GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        categories_dict = create_categories_dict(categories)

        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    # Create an endpoint to handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint should return a list of questions,
    # number of total questions, current category, categories.
    #
    # TEST: At this point, when you start the application
    # you should see questions and categories generated,
    # ten questions per page and pagination at the bottom of the screen for three pages.
    # Clicking on the page numbers should update the questions.
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()

        if len(questions) == 0:
            abort(404)
        elif len(categories) == 0:
            abort(404)

        pagination = paginate_questions(questions)

        categories_dict = create_categories_dict(categories)

        return jsonify({
            'success': True,
            'questions': pagination,
            'total_questions': len(questions),
            'current_category': 5, # TODO: add functionality
            'categories': categories_dict
        })

    # @TODO:
    # Create an endpoint to DELETE question using a question ID.
    #
    # TEST: When you click the trash icon next to a question, the question will be removed.
    # This removal will persist in the database and when you refresh the page.

    # @TODO:
    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.
    #
    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of the last page
    # of the questions list in the "List" tab.

    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.
    #
    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.

    # @TODO:
    # Create a GET endpoint to get questions based on category.
    #
    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.

    # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    #
    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.

    # Create error handlers for all expected errors including 404 and 422.
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app