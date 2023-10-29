from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__, template_folder='/data/IMP_Projects/Flask_projects/To_DoList/app/templates')
# app.secret_key = "your_secret_key"  # Replace with a secure secret key


# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'  # Replace with your MySQL server details
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
mysql = MySQL(app)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password,phone) VALUES (%s, %s, %s)", (username, password, phone))
        mysql.connection.commit()
        cur.close()

        session['username'] = username
        return redirect(url_for('profile'))
    return render_template('signup.html')


@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        return jsonify({"message": f'Logged in as {username}'})
    return jsonify({"error": 'Your are not logged in'})


@app.route('/welcome')
def welcome():
    if 'username' in session:
        username = session['username']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username]) #this query is for getting username to show username in welcomepage
        user = cur.fetchone()
        userid = user[0]
        cur.execute("SELECT * FROM tasks WHERE user_id = %s", [userid])  # this query is for getting taskscreaed by the user by id (fk)to show in frontpanel
        tasks = cur.fetchall()
        cur.close()
                
        return render_template('welcome.html', username=username, userdata=user, tasks=tasks )
    else:
        return "seesion time out"



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()

        if user and user[2] == password:  # user[2] is the password field in the database
            session['username'] = username
            return redirect(url_for('profile'))
        else:
             return jsonify({"error": 'You have provided wrong credentials'})


    return render_template('index.html')


@app.route('/createtask', methods=['POST'])
def create():
    if request.method == 'POST':
        data = request.json
        userid = data.get('userid')
        task = data.get('task')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (user_id, task_name) VALUES (%s, %s)", (userid, task))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": 'Your Task has been Succesfully created'})
    
    return jsonify({"error": 'Error During Creating Tasks'})



@app.route('/updatetask', methods=['POST'])
def updatetask():
    if request.method == 'POST':
        data = request.json
        taskid = data.get('tasksid')
        taskdesc = data.get('taskdesc')
        taskstatus = data.get('taskstatus')

        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks set task_name =(%s) , status = (%s) where id =(%s)",(taskdesc,taskstatus,taskid))

        mysql.connection.commit()
        cur.close()
        return jsonify({"message": 'Your Task has been Succesfully updated'})
    
    return jsonify({"error": 'Error During Updating Tasks'})



@app.route('/deletetask', methods=['POST'])
def deletetask():
    if request.method == 'POST':
        data = request.json
        taskid = data.get('tasksid')

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tasks where id =(%s)",(taskid))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": 'Your Task has been Deleted'})
    
    return jsonify({"error": 'Error During Deleting Tasks'})



@app.route('/logout',methods=['GET'])
def logout():
    session.pop('username', None)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)