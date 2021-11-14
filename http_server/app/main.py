"""
http server для доступа к данным
"""
import os
from flask import Flask, render_template

from Api.views import betcsgo
from config   import PRODUCTION_WORK
from waitress import serve
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.register_blueprint( betcsgo )


@app.route('/')
def index():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    return "<h1>Flask Main</h1> <p> It is currently {} </p>".format( the_time )

@app.errorhandler(404)
def error_404(error):
    return "404 Not found", 404
    # return render_template("404.html", error=error, code_error = 404), 404



def app_run():
    if PRODUCTION_WORK:
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(port=5000, host='0.0.0.0', debug=True)

if __name__ == '__main__':
    app_run()