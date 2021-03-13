
from logging import error
import os
import re
from flask import Flask, json, request, abort, jsonify, redirect
from flask.globals import session
from flask.helpers import url_for
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

import sqlalchemy
from sqlalchemy.orm import load_only
from werkzeug.exceptions import NotFound

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"api":{"origins":"*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('ACCESS-CONTROL-ALLOW-ORIGIN', "*")
    response.headers.add('ACCESS-CONTROL-ALLOW-HEADER','Content-Type')
    response.headers.add('ACCESS-CONTROL-ALLOW-METHODS', 'GET, POST, PATCH, DELETE, PUT')
    return response
  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    try:
      categories = Category.query.all()
      cat_list = [category.type for category in categories]
      return jsonify({
        'categories' : cat_list,
        'success':True
      })
    except:
      abort(422)

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions')
  def show_questions():
    try:
      page = request.args.get('page', 1, int)
      start = (page-1)*10
      end = start+10
      Questions = Question.query.all()
      questions = [question.format() for question in Questions]
      Categories = Category.query.all()
      categories = [category.type for category in Categories]
      maxPages = int(len(questions)/10)+1
      print("page: ",page)
      print("max number of pages: ",maxPages)
      if (page > maxPages):
        abort()
       
      return jsonify(  {
        'format':questions[start:end],
        'total_questions': len(questions),
        'categories': categories,
        'success' : True
        })
    except:
      if (page > maxPages):
        abort(404)
      abort(422)
  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question =Question.query.filter_by(id = id).one_or_none()
      if question is None:
        abort()
      question.delete()
      return jsonify({"success": True})
    except:
      if question is None:
        abort(404)
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
  @app.route('/questions/add', methods=['POST'])
  def add_question():
    try:
      question = request.get_json()['question']
      answer = request.get_json()['answer']
      difficulty = request.get_json()['difficulty']
      category = request.get_json()['category']
      print("category: ",category)
      category=int(category)
      print("category: ",category)
      _question = Question(question, answer,category , difficulty)
      _question.insert()
      return jsonify({"success": True})
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
    try:
      searchTerm = request.get_json()['searchTerm']
      Results = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()
      searchResults = [question.format() for question in Results]
      return jsonify({
        'questions': searchResults,
        'totalQuestions': len(searchResults),
        'currentCategory': 'a',
        'success':True
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
  @app.route('/categories/<int:ID>/questions')
  def filter_by_category(ID):
    try:
      Results = Question.query.filter_by(category= ID+1).all()
      searchResults = [question.format() for question in Results]
      return jsonify({
        'questions': searchResults,
        'totalQuestions': len(searchResults),
        'currentCategory': 'a',
        'success': True
      })
    except:
      abort(422)

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
  def get_question():
    try:
      category = request.get_json()['quiz_category']
      previousQuestions = request.get_json()['previous_questions']
      Results = Question.query.filter_by(category= category['id']).all()
      searchResult = [question.format() for question in Results]
      
      if len(previousQuestions) == len(searchResult):
        return jsonify({
          'message':'finish'
        })
      return jsonify({
        'question': searchResult[len(previousQuestions)],
        'currentCategory': 'a',
        'success':True
      })
    except:
      abort(422)
  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(e):
    return jsonify({
        'success' : False,
        'error':404,
        'message':'Not Found'
      }),404

  @app.errorhandler(422)
  def unprocessable(e):
    return jsonify({
        'success' : False,
        'error':422,
        'message':'Unprocessable Entity'
      }),422

  @app.errorhandler(405)
  def not_allowed(e):
    return jsonify({
        'success' : False,
        'error':405,
        'message':'Method Not Allowed'
      }),405

  return app