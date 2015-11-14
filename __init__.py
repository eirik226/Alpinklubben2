
import os
import sqlite3

from flask import Flask, render_template, flash, request, g, url_for, redirect, session, escape, abort, jsonify
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt

import gc

#from dbconnect import connection
#from content_management import Content

#TOPIC_DICT = Content()

# konfigurasjon av globale variable
DATABASE = 'alpinklubben.db'
DEBUG = True
SECRET_KEY = 'Qh\x84J\xbb^\xeb\x8d\x96\x07\xa1\xf2Q\x905(\xbca\x06\x13\x1a\xb5\xf6\xad'

# lager og initialiserer appen
app = Flask(__name__)
app.config.from_object(__name__)
@app.route('/', methods=['GET', 'POST'])


@app.route('/')
def homepage():
    return render_template("forside.html")




class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(), 
    validators.EqualTo('confirm', message="Passordene er ikke like.")])
    confirm = PasswordField('Gjenta Passord')

@app.route('/registrer', methods=['GET','POST'])
def registrer_side():
    try:
        form = RegistrationForm(request.form)
        db = sqlite3.connect('alpinklubben.db')
        cursor = db.cursor()
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            

            x = cursor.execute('''SELECT * FROM users WHERE username = ?''')
            if int(x) > 0:
                flash("Dette brukernavnet eksisterer - velg et annet")
                return render_template('registrer.html', form=form)
            else:
              db.execute('''INSERT INTO users(username, email, password) VALUES(?, ?, ?)''',
              (username, email, 'password'))
              db.commit()
              flash('Takk for at du registrerte deg')
              #db.close()
              #gc.collect()

              session['logget_inn'] = True
              session['username'] = username

              return redirect(url_for('index'))
        return render_template("registrer.html", form=form)
    except Exception as e:
        return (str(e))




@app.route('/login', methods = ['GET','POST'])
def login_page():
    error = ''
    try:
        if request.method == "POST":
            attemted_username = request.form['brukernavn']
            attemted_password = request.form['passord']
            #flash(attempted_username)
            #flash(attempted_password)
    
            if attempted_username == "admin" and attempted_password == "admin":
                return redirect(url_for('index'))
            else:
                error = 'Feil innloggingsinformasjon - prov igjen'
        return render_template("login.html", error = error)
	
    except Exception as e:
        #flash(e)
        return render_template("login.html", error = error)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")

# kobler til databasen
def connect_db():
    """Kobler til databasen."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
 
# lager databasen
def init_db():
    with app.app_context():
      db = get_db()
      with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
      db.commit()
	
# aapner forbindelsen til databasen
def get_db():
    if not hasattr(g, 'sqlite_db'):
      g.sqlite_db = connect_db()
    return g.sqlite_db
 
# lukker forbindelsen til databasen
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
      g.sqlite_db.close()


if __name__ == "__main__": #Kanskje bruke login her?
    init_db()
    app.run(debug=True)