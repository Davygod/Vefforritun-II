from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import pallar
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

pallar = pallar()

app.route('/')
def index():
  return render_template('index.html')

# pallar
@app.route('/pallar.html')
def pallar():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get pallar
    result = cur.execute("SELECT * FROM pallar")

    pallar = cur.fetchall()

    if result > 0:
        return render_template('pallar.html', pallar=pallar)
    else:
        msg = 'No pallar Found'
        return render_template('pallar.html', msg=msg)
    # Close connection
    cur.close()


#Single leikur
@app.route('/pallar/<string:id>/')
def leikur(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get leikur
    result = cur.execute("SELECT * FROM pallar WHERE id = %s", [id])

    leikur = cur.fetchone()

    return render_template('leikur.html', leikur=leikur)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/buaTilAdgang', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('skraInn'))
    return render_template('buaTilAdgang.html', form=form)


# User skraInn
@app.route('/skraInn.html', methods=['GET', 'POST'])
def skraInn():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid skraInn'
                return render_template('skraInn.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('skraInn.html', error=error)

    return render_template('skraInn.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please skraInn', 'danger')
            return redirect(url_for('skraInn'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('skraInn'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get pallar
    #result = cur.execute("SELECT * FROM pallar")
    # Show pallar only from the user logged in 
    result = cur.execute("SELECT * FROM pallar WHERE author = %s", [session['username']])

    pallar = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', pallar=pallar)
    else:
        msg = 'No pallar Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

# leikur Form Class
class leikurForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add leikur
@app.route('/add_leikur', methods=['GET', 'POST'])
@is_logged_in
def add_leikur():
    form = leikurForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO pallar(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('leikur Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_leikur.html', form=form)


# Edit leikur
@app.route('/edit_leikur/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_leikur(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get leikur by id
    result = cur.execute("SELECT * FROM pallar WHERE id = %s", [id])

    leikur = cur.fetchone()
    cur.close()
    # Get form
    form = leikurForm(request.form)

    # Populate leikur form fields
    form.title.data = leikur['title']
    form.body.data = leikur['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)
        # Execute
        cur.execute ("UPDATE pallar SET title=%s, body=%s WHERE id=%s",(title, body, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('leikur Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_leikur.html', form=form)

# Delete leikur
@app.route('/delete_leikur/<string:id>', methods=['POST'])
@is_logged_in
def delete_leikur(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM pallar WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('leikur Deleted', 'success')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)