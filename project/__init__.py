#import flask - from package import class
from flask import Flask, render_template, session
from flask_bootstrap import Bootstrap5
from flask_mysqldb import MySQL

mysql = MySQL()

#create a function that creates a web application
# a web server will run this web application
def create_app():
    app = Flask(__name__)
    app.debug = False
    app.secret_key = 'BetterSecretNeeded123'
    # MySQL configurations
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Tanish@123'
    app.config['MYSQL_DB'] = 'sharespace'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)

    bootstrap = Bootstrap5(app)
    
    #importing modules here to avoid circular references, register blueprints of routes
    from . import views
    app.register_blueprint(views.bp)

    @app.errorhandler(400)
    def bad_request(e):
      return render_template(
          "error.html",
          code=400,
          title="Bad request",
          message="The request could not be processed. Please try again."
      ), 400

    @app.errorhandler(403)
    def forbidden(e):
      return render_template(
          "error.html",
          code=403,
          title="Access denied",
          message="You do not have permission to view this page."
      ), 403

    @app.errorhandler(404)
    def not_found(e):
      return render_template(
          "error.html",
          code=404,
          title="Page not found",
          message="Sorry, we cannot find what you are looking for."
      ), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
      return render_template(
          "error.html",
          code=405,
          title="Method not allowed",
          message="This action is not available from this page."
      ), 405

    @app.errorhandler(500)
    def internal_error(e):
      return render_template(
          "error.html",
          code=500,
          title="Internal server error",
          message="Sorry, the server encountered an error. Please try again in a few minutes."
      ), 500


    return app
