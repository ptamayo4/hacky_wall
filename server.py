from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
mysql = MySQLConnector(app,'wall')
# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app.secret_key = "KeepItSecret"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    # Do our validations on the input
    if EMAIL_REGEX.match(request.form['email']) and request.form['password'] >= 8 and request.form['password'] == request.form['confirm_password']:
        # encrypt password asap
        data = {
            "first_name" : request.form['first_name'],
            "last_name"  : request.form['last_name'],
            "email"      : request.form['email'],
            "password"   : request.form['password']
        }

        query = "INSERT INTO users(first_name,last_name,email,password,created_at,updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        print mysql.query_db(query,data)
        get_id = mysql.query_db('select id, first_name, last_name from users where email=:email and password=:password',data)
        print get_id
        session['id'] = get_id[0]
        print session['id']
        return redirect('/wall')

    print "Errors"
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = mysql.query_db("SELECT password FROM users WHERE email = '{}'".format(email))
    print password
    password = password[0]['password']
    print password

    pass_to_check = request.form['password']
    if password == pass_to_check:
        print "correct password and email combo"
        data = { 'password': password, 'email': request.form['email']}
        get_id = mysql.query_db('SELECT id, first_name, last_name FROM users WHERE email=:email and password=:password',data)
        session['id'] = get_id[0]
        print session['id']
        return redirect('/wall')

    print "wrong password or email"
    return redirect('/')

@app.route('/logout', methods=['POST'])
def logout():
    print session
    session.pop('id', None)
    print session
    return redirect('/')

@app.route('/wall')
def wall():
    if not session.get('id'):
        return redirect('/')

    all_messages = mysql.query_db("select users.id as user_id, first_name, last_name, messages.id, message, messages.created_at from users join messages on messages.user_id = users.id order by messages.created_at desc;")
    all_comments = mysql.query_db("select message_id, user_id, comment, first_name, last_name, comments.created_at from comments join users on user_id = users.id order by comments.created_at asc;")

    return render_template('wall.html', messages=all_messages, comments=all_comments)

@app.route('/message', methods=['POST'])
def add_message():
    query = ("insert into messages(user_id, message, created_at, updated_at) values (:user_id, :message, NOW(), NOW())")
    data = { "user_id": session['id']['id'], "message":request.form['message'] }
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/comment', methods=['POST'])
def add_comment():
    query = ("insert into comments(user_id, message_id, comment, created_at, updated_at) values (:user_id, :message_id, :comment, NOW(), NOW())")
    data = {"user_id":session['id']['id'], "message_id":request.form['message_id'], "comment": request.form['comment'] }
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/delete', methods=['POST'])
def delete_message():
    query = "delete from comments where message_id=:message_id"
    data = {"message_id":request.form['message_id']}
    mysql.query_db(query, data)

    query = "delete from messages where id=:message_id"
    mysql.query_db(query,data)
    return redirect('/wall')






app.run(debug=True)
