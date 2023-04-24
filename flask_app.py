from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from datetime import timedelta, datetime
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from multipledispatch import dispatch
app = Flask(__name__)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'ERROR_706')

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
class LoginUser(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)
def add_player(Pname, PEmail, Phno, PAge,Password):
    con = sqlite3.connect("Elitmusdb.db")
    cur = con.cursor()
    try:
        x = (Pname, PEmail, Phno, PAge,Password)
        insert = """INSERT INTO Users (Pname, PEmail, Phno, PAge, Password) VALUES (?,?,?,?,?);"""
        cur.execute(insert, x)
    finally:
        con.commit()
        cur.close()
        con.close()
        curr_user.set_user()

def get_new_user():
    con = sqlite3.connect("Elitmusdb.db")
    cur = con.cursor()
    try:
        sql_select_query = "select max(Pid) from Users;"
        cur.execute(sql_select_query)
        record = cur.fetchall()
    finally:
        con.commit()
        cur.close()
        con.close()
    return record[0]

def get_player(Pid):
    con = sqlite3.connect("Elitmusdb.db")
    cur = con.cursor()
    try:
        sql_select_query = "select * from Players where Pid = ?;"
        cur.execute(sql_select_query, (Pid,))
        record = cur.fetchall()
    finally:
        con.commit()
        cur.close()
        con.close()
    return record[0]

def update_player():
    con = sqlite3.connect("Elitmusdb.db")
    cur = con.cursor()
    try:
        x = (curr_user.Pname, curr_user.PEmail, curr_user.Phno,curr_user.PAge,curr_user.PStart,curr_user.PStop,curr_user.PMarks)
        insert = """INSERT INTO Players ( Pname, PEmail, Phno, PAge,PStart,PStop,PMarks) VALUES (?,?,?,?,?,?,?);"""
        cur.execute(insert, x)
    finally:
        con.commit()
        cur.close()
        con.close()
        
def check_email_exists(PEmail):
    con = sqlite3.connect("Elitmusdb.db")
    c = con.cursor()
    try:
        sql_select_query = "select * from Users where PEmail = ?;"
        c.execute(sql_select_query, (PEmail,))
        record = c.fetchall()   
    finally:
        con.commit()
        c.close()
        con.close()
    if len(record) == 0:
        return False
    else:
        return True
    
def get_user_details(PEmail):
    con = sqlite3.connect("Elitmusdb.db")
    c = con.cursor()
    try:
        sql_select_query = "select * from Users where PEmail = ?;"
        c.execute(sql_select_query, (PEmail,))
        record = c.fetchall()
    finally:
        con.commit()
        c.close()
        con.close()
    return record[0]

def get_players_played():
    con = sqlite3.connect("Elitmusdb.db")
    cur = con.cursor()
    try:
        sql_select_query = "select * from Players where PStart > 0 and PStop > 0 order by Pid desc;"
        cur.execute(sql_select_query)
        record = cur.fetchall()
    finally:
        con.commit()
        cur.close()
        con.close()
    return record
  
class Curr_User:
    def __init__(self):
        self.Pid = self.Pname = self.PAge = self.PEmail = self.Phno = self.Password =self.PStart=self.PStop=self.PMarks= False
    @dispatch()
    def set_user(self):
        self.Pid = get_new_user()[0]
        record = get_player(self.Pid)
        self.Pname = record[1]
        self.PEmail = record[2]
        self.Phno = record[3]
        self.PAge = record[4]
        self.Password=record[5]
    @dispatch(int,str,str,int,int,str)
    def set_user(self,Pid,Pname,PEmail,Phno,PAge,Password):
        self.Pid=Pid
        self.Pname=Pname
        self.PEmail=PEmail
        self.Phno=Phno
        self.PAge=PAge
        self.Password=Password 
    
    def set_start(self):
        PStart = datetime.now()
        PStart = datetime.strftime(PStart, "%H:%M:%S")
        self.PStart = datetime.strptime(PStart, "%H:%M:%S")
    def set_stop(self):
        PStop = datetime.now()
        PStop = datetime.strftime(PStop, "%H:%M:%S")
        self.PStop = datetime.strptime(PStop, "%H:%M:%S")
    def set_marks(self, PScore):
        self.PMarks = PScore
    def time(self):
        return str(self.PStop - self.PStart).split(":")
    
curr_user = Curr_User()
@app.route("/")
def index():
    return render_template("Home.html")
@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        Pname = request.form["Pname"]
        PEmail = request.form["PEmail"]
        Phno = request.form["Phno"]
        PAge = request.form["PAge"]
        Password=request.form['Pwd']
        add_player(Pname, PEmail, Phno, PAge,Password)
        curr_user.set_start()
        return redirect(url_for("game"))
    return render_template("Signup.html")

@app.route('/game', methods = ["POST", "GET"])
@login_required
def game():
    if request.method == "POST":
        req = request.form
        score = 0
        for key in req.keys():
            if req[key] == "1":
                score += 1      
        curr_user.set_stop()
        curr_user.set_marks(score)
        update_player()
        return redirect(url_for('score'))
    return render_template("Game.html")

@app.route('/score')
@login_required
def score():
    return render_template("Score.html", time = curr_user.time(), score = curr_user.PMarks)

@app.route('/admin_login', methods = ['POST', 'GET'])
@login_required
def admin_login():
    if request.method == "POST":
        req = request.form
        if req["user"] == "Admin@gmail.com" and req["pwd"] == "123456":
            admin_user.set_login()
            return redirect(url_for("admin"))
        
        else:
            return render_template("admin_login.html", info = "Wrong Username or Password")
    return render_template("Admin_Login.html")

class AdminUSER:
    def __init__(self):
        self.status = False
    def set_login(self):
        self.status = True
    def set_logout(self):
        self.status = False
    def get_status(self):
        return self.status
admin_user = AdminUSER()

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        PEmail = request.form['email']
        pwd = request.form['pwd']
        if check_email_exists(PEmail) == False:
            return render_template('login.html', info='Email Does Not Exist!!!')
        record = get_user_details(PEmail)
        if record[5] != pwd:
            return render_template('login.html', info='Invalid Password!!!')
        else:
            logged_user = LoginUser(PEmail + pwd)
            curr_user.set_user(record[0], record[1], record[2], record[3], record[4], record[5])
            login_user(logged_user)
            curr_user.set_start()
            return redirect(url_for('game'))
    return render_template('login.html')

@app.route("/admin")
def admin():
    if admin_user.get_status():
        records = get_players_played()
        new_records = []
        for record in records:
            record = list(record)
            start = record[5].split(" ")
            stop = record[6].split(" ")
            start, stop = datetime.strptime(start[1], "%H:%M:%S"), datetime.strptime(stop[1], "%H:%M:%S")
            record.append(str(stop - start).split(":"))
            new_records.append(record)
        return render_template("Admin.html", records = new_records)
    else:
        return redirect(url_for('index'))
@app.route("/adminlogout")
def adminLogout():
    admin_user.set_logout()
    return redirect(url_for("index"))
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(userid):
    return LoginUser(userid)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True
    g.user = current_user

if __name__=='__main__':
    app.run(debug=True)
