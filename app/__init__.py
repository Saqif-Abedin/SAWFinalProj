from flask import Flask, render_template, request, session, url_for, redirect, abort
from flask_bcrypt import Bcrypt
import bcrypt
import os
from datetime import datetime
import sqlite3
import uuid

#test comment
APP_NAME = "TeamSAW Personal Expense Tracker"
app = Flask(APP_NAME, template_folder="app/templates", static_folder="app/static")
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(32)
DB_FILE = "app/team_saw.db"
db = sqlite3.connect(DB_FILE, check_same_thread = False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, user_id TEXT NOT NULL UNIQUE, username TEXT NOT NULL UNIQUE, password	TEXT NOT NULL, budget TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses(ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, user_id TEXT NOT NULL, expense_name TEXT NOT NULL, desc TEXT NOT NULL, amount DOUBLE NOT NULL, timestamp TEXT)')

@app.route("/")
def renderlogin():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    if not request.form.get("username") or not request.form.get("password"):
        return render_template("error.html", warning="Please fill out all fields.")
    elif len(request.form.get("password")) < 4:
        return render_template("error.html", warning="Password must be at least 4 characters long.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    if user:
        db.close()
        return render_template("error.html", warning="Username is already taken.")

    password_hash = bcrypt.generate_password_hash(request.form.get("password"))
    user_id = str(uuid.uuid4())
    if request.form.get("budget"):
        cursor.execute("insert into users (user_id, username, password, budget) values (?, ?, ?, ?)", (user_id, request.form.get("username"), password_hash, request.form.get("budget")))
    else:
        cursor.execute("insert into users (user_id, username, password, budget) values (?, ?, ?,?)", (user_id, request.form.get("username"), password_hash, 0))
    cursor.execute("select * from users where user_id = ?", (user_id,))
    user = cursor.fetchone()
    db.commit()
    c.execute('select expense_name, desc, amount, timestamp from expenses where user_id=?', (user_id,)) 
    expenses = c.fetchall()
    c.execute('select budget from users where user_id=?', (user_id,))
    budget = float(c.fetchone()[0])
    db.close()

    session["user_id"] = user[1]
    session["username"] = user[2]
    session['budget'] = budget
    session['expenses'] = expenses
    return render_template("main.html", table = expenses, budget = budget)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("index"))
        return render_template("login.html")

    if not request.form.get("username") or not request.form.get("password"):
        return render_template("error.html", warning="Please fill out all fields.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    db.close()
    if not user or not bcrypt.check_password_hash(user[3], request.form.get("password")):
        return render_template("error.html", warning="Incorrect username or password.")

    session["user_id"] = user[1]
    session["username"] = user[2]
    user_id = session["user_id"]
    c.execute('select expense_name, desc, amount, timestamp from expenses where user_id=?', (user_id,)) 
    expenses = c.fetchall()
    c.execute('select budget from users where user_id=?', (user_id,))
    budget = float(c.fetchone()[0])
    session['budget'] = budget
    session['expenses'] = expenses
    return render_template("main.html", table = expenses, budget = budget)


@app.route("/logout")
def logout():
    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    session.pop("user_id")
    session.pop("username")
    return redirect(url_for("index"))

@app.route("/addentry")
def addentry():
    user_id = session["user_id"]
    expense_name = request.args.get("expense_name")
    expense_desc = request.args.get("expense_desc")
    expense_amount = float(request.args.get("expense_amount"))
    today = datetime.today().strftime('%Y-%m-%d-%H:%M')
    c.execute('insert into expenses(user_id, expense_name, desc, amount, timestamp) values(?,?,?,?,?)', (user_id, expense_name, expense_desc, '${:,.2f}'.format(expense_amount), today))
    db.commit()
    c.execute('select expense_name, desc, amount, timestamp from expenses where user_id=?', (user_id,)) 
    expenses = c.fetchall()
    session['expenses'] = expenses
    budget = session["budget"] - expense_amount
    session["budget"] = budget
    c.execute('update users set budget=?', (budget,))
    db.commit()
    return render_template("main.html", table = expenses, budget = '${:,.2f}'.format(budget))

@app.route("/setbudget")
def setbudget():
    user_id = session["user_id"]
    budget = float(request.args.get("budget"))
    c.execute('update users set budget=? where user_id =? ', (budget, user_id))
    session["budget"] = budget
    c.execute('delete from expenses where user_id=?', (user_id,))
    db.commit()
    return render_template('main.html', budget = '${:,.2f}'.format(budget))




if __name__ == "__main__":
    app.debug = True
    app.run()
