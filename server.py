from flask import Flask, render_template, redirect, session, request, flash
from mysqlconnection import connectToMySQL
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "ja98sd71j2kla8lk2m390a21k"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    errors = []
    session['email'] = request.form['email']

    if len(request.form['email']) < 1 or not EMAIL_REGEX.match(request.form['email']):
        errors.append("Invalid Email Address!")
    
    
    mysql = connectToMySQL('emailsdb')
    email_query = 'SELECT * FROM emails WHERE email = %(email)s;'
    data = {
        'email': request.form['email']
    }
    emails = mysql.query_db(email_query, data)

    if len(emails) > 0:
        errors.append('Email is already in use!')

    if len(errors) > 0:
        for error in errors:
            flash(error, "error")
        return redirect('/')
    else:
        mysql = connectToMySQL('emailsdb')
        insert_query = 'INSERT INTO emails (email, created_at) VALUES (%(email)s, NOW());'
        insert_data = {
            'email': request.form['email']
        }
        email = mysql.query_db(insert_query, insert_data)
        return redirect('/success')

@app.route('/success')
def success():
    mysql = connectToMySQL('emailsdb')
    all_emails = mysql.query_db("SELECT id, email, DATE_FORMAT(created_at, '%m/%d/%y %r') AS created_at FROM emails;")
    return render_template('success.html', emails=all_emails)
    
@app.route('/<email_id>/delete', methods=['POST'])
def delete(email_id):
    mysql = connectToMySQL('emailsdb')
    delete_query = "DELETE FROM emails WHERE id=%(id)s;"
    data = {
        'id': email_id
    }
    mysql.query_db(delete_query, data)
    return redirect('/success')
 
if __name__=="__main__":
    app.run(debug=True)