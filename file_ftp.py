#!/user/bin/python

DEBUG = True
PORT = 8085
AUTHORIZED_METHODS = ['GET' , 'POST']
from flask import Flask , render_template
import time
time.sleep(30)
app = Flask(__name__)


@app.route('/')
def show_index():
    return "you can find images here"


if __name__ == '__main__':
    app.run(debug=DEBUG , port=PORT , host='0.0.0.0')
