from flask import Flask, render_template
from data import Articles

app = Flask(__name__)

Articles = Articles()

app.route('/')
def index():
  return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)