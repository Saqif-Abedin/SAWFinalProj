from flask import Flask, render_template, request, session, url_for, redirect, abort
from flask_bcrypt import Bcrypt
import bcrypt
import os
import time
import sqlite3
import uuid

#test comment
APP_NAME = "TeamSAW Personal Expense Tracker"
app = Flask(APP_NAME, template_folder="app/templates", static_folder="app/static")
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(32)
DB_FILE = "app/team_saw.db"


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirm password"):
        return render_template("register.html", warning="Please fill out all fields.")
    elif len(request.form.get("password")) < 4:
        return render_template("register.html", warning="Password must be at least 4 characters long.")
    elif request.form.get("password") != request.form.get("confirm password"):
        return render_template("register.html", warning="Passwords do not match.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    if user:
        db.close()
        return render_template("register.html", warning="Username is already taken.")

    password_hash = bcrypt.generate_password_hash(request.form.get("password"))
    user_id = str(uuid.uuid4())
    if request.form.get("description"):
        cursor.execute("insert into users (user_id, username, password, description) values (?, ?, ?, ?)", (user_id, request.form.get("username"), password_hash, request.form.get("description")))
    else:
        cursor.execute("insert into users (user_id, username, password) values (?, ?, ?)", (user_id, request.form.get("username"), password_hash))
    cursor.execute("select * from users where user_id = ?", (user_id,))
    user = cursor.fetchone()
    db.commit()
    db.close()

    session["user_id"] = user[1]
    session["username"] = user[2]
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("index"))
        return render_template("login.html")

    if not request.form.get("username") or not request.form.get("password"):
        return render_template("login.html", warning="Please fill out all fields.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    db.close()
    if not user or not bcrypt.check_password_hash(user[3], request.form.get("password")):
        return render_template("login.html", warning="Incorrect username or password.")

    session["user_id"] = user[1]
    session["username"] = user[2]
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    session.pop("user_id")
    session.pop("username")
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.debug = True
    app.run()
