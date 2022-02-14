from flask import Flask, render_template, flash, redirect, url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

Articles = Articles()

app.route('/')
def index():
  return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)