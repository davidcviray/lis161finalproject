from flask import Flask, request, jsonify, url_for, redirect, session, render_template, g
import sqlite3

app = Flask(__name__)  # Creates Flask App

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Thisisasecret!'


def connect_db():  # Connects to SQL Database
    sql = sqlite3.connect('/Users/Constantine/data.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():  # Retrieves Database
    if not hasattr(g, 'sqlite3'):  # Appends sqlite3 to g
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):  # Closes Database
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET'], defaults={'name': 'guest'})  # Homepage, sets default session as guest
@app.route('/<string:name>', methods=['POST', 'GET'])  # Retrieves username after login
def main(name):
    session['name'] = name  # Creates session
    db = get_db()  # Retrieves database
    cur = db.execute('select libid, library, status from libs')  # Fetches library list
    results = cur.fetchall()
    if name == 'guest':
        return render_template('main.html', name=name, results=results, display=False)  # Loads the homepage template
    else:
        return redirect(url_for('loggedin', name=name, results=results, display=True))  # Redirects to loggedin


@app.route('/loggedin<string:name>', methods=['POST', 'GET'])
def loggedin(name):
    session['name'] = name  # Creates session
    db = get_db()  # Retrieves database
    cur = db.execute('select libid, library, status from libs')  # Fetches library list
    results = cur.fetchall()
    return render_template('loggedin.html', name=name, results=results, display=True)  # Loads the logged in page


@app.route('/logout')  # Logs out the user
def logout():
    session.pop('name', None)  # Pops their current session
    return redirect(url_for('main'))  # Brings them back to homepage


@app.route('/login', methods=['POST', 'GET'])  # Creates the login page
def login():
    if request.method == 'GET':
        return render_template('login.html')  # Loads the login template
    if request.method == 'POST':
        uname = request.form['uname']
        psw = request.form['psw']

        db = get_db()
        cur = db.execute('select * from user where username = ? and password = ?',
                         [uname, psw])  # looks for username and password combination
        results = cur.fetchall()
        if len(results) == 0:  # checks if there's a match
            return render_template('login.html', display=True)
        else:
            return redirect(url_for('loggedin', name=uname))


@app.route('/add', methods=['POST', 'GET'])
def add():
    name = session.get('name', None)  # Retrieve current session
    if request.method == 'GET':
        return render_template('add.html')  # Loads the add page if not posting
    if request.method == 'POST':
        library = request.form['library']  # retrieve library name
        status = request.form['status']  # retrieve status

        db = get_db()
        db.execute('insert into libs (library,status) values (?,?)', [library, status])  # SQL Command Insert new user
        db.commit()  # Push SQL Changes
        return redirect(url_for('loggedin', name=name))

@app.route('/edit', methods=['POST', 'GET'])
def edit():
    name = session.get('name', None)  # Retrieve current session
    if request.method == 'GET':
        return render_template('edit.html')  # Loads the add page if not posting
    if request.method == 'POST':
        libid = request.form['libid']
        library = request.form['library']  # retrieve library name
        status = request.form['status']  # retrieve status

        db = get_db()
        db.execute('update libs set library = ?, status = ? where libid = ?',
                    [library, status,libid])  # SQL Command Edit library row
        db.commit()  # Push SQL Changes
        return redirect(url_for('loggedin', name=name))

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    name = session.get('name', None)  # Retrieve current session
    if request.method == 'GET':
        return render_template('delete.html')  # Loads the add page if not posting
    if request.method == 'POST':
        libid = request.form['libid']
        db = get_db()
        db.execute('delete from libs where libid = ?', [libid])  # SQL Command Edit library row
        db.commit()  # Push SQL Changes
        return redirect(url_for('loggedin', name=name))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')  # if GET request, display form
    else:  # if POST request, load database
        uname = request.form['uname']  # retrieve username from form
        psw = request.form['psw']  # retrieve password from form

        db = get_db()
        db.execute('insert into user (username,password) values (?,?)', [uname, psw])  # SQL Command Insert new user
        db.commit()  # Push SQL Changes

        return redirect(url_for('login'))


if __name__ == '__main__':  # Runs the Application
    app.run()
