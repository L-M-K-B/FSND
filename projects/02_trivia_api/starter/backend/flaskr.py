from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from sqlalchemy.exc import SQLAlchemyError

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

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)
    return d


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
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()

        if len(questions) == 0:
            abort(404)
        elif len(categories) == 0:
            abort(404)

        categories_dict = create_categories_dict(categories)

        return jsonify({
            'success': True,
            'questions': paginate_questions(questions),
            'total_questions': len(questions),
            'categories': categories_dict
        })

    # Create an endpoint to DELETE question using a question ID.
    @app.route('/question/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if not question:
                abort(422)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
            })
        except SQLAlchemyError:
            abort(422)

    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.
    @app.route('/question', methods=['POST'])
    def create_question():
        question = request.get_json()['question']
        answer = request.get_json()['answer']
        difficulty = request.get_json()['difficulty']
        category = request.get_json()['category']

        try:
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()

            return jsonify({
                'success': True,
                'created': new_question.id
            })
        except SQLAlchemyError:
            abort(405)

    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        search_term = request.get_json()['searchTerm']

        try:
            suggestions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            if not suggestions:
                abort(404)

            return jsonify({
                'success': True,
                'questions': paginate_questions(suggestions),
                'total_questions': len(suggestions)
            })
        except SQLAlchemyError:
            abort(422)

    # Create a GET endpoint to get questions based on category.
    @app.route('/category/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category == category_id).all()

            if not questions:
                abort(404)

            return jsonify({
                'success': True,
                'questions': paginate_questions(questions),
                'total_questions': len(questions)
            })
        except SQLAlchemyError:
            abort(422)

    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        previous_questions = request.get_json()['previous_questions']
        quiz_category = int(request.get_json()['quiz_category'])

        try:
            if quiz_category:
                suggestions = Question.query \
                    .filter(Question.category == quiz_category) \
                    .filter(Question.id.notin_(previous_questions)) \
                    .all()
            else:
                suggestions = Question.query.filter(Question.id.notin_(previous_questions)).all()

            if not suggestions:
                new_question = None
            else:
                new_question = row2dict(random.choice(suggestions))

            return jsonify({
                'success': True,
                'question': new_question,
            })
        except SQLAlchemyError:
            abort(422)

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
