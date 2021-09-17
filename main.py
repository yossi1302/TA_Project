from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import random
import requests,json
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import flash
import speech_recognition as sr

app = Flask( 
	__name__,
	template_folder='templates', 
	static_folder='static'  
)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class users(db.Model):
  _id = db.Column('id', db.Integer, primary_key=True)
  username = db.Column(db.String(100))
  password = db.Column(db.String(100))
  keyword = db.Column(db.String(100))

  def __init__(self, username, password, keyword):
    self.username = username
    self.password = password
    self.keyword = keyword
  
@app.route('/',methods=['GET', 'POST'])  
def login():
  if request.method == 'GET':
    return render_template('login.html')
  else:
    temp_username = request.form['username']
    temp_password = request.form['password']
    found_user = users.query.filter_by(username = temp_username).first()
    if found_user and found_user.password == temp_password:
      try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
          audio = r.listen(source)
          voice_data = r.recognize_google(audio)
          if voice_data == found_user.keyword:
            return redirect(url_for('home'))
          else:
            flash("wrong word")
            return render_template('login.html')
      except sr.UnknownValueError:
        flash("I did not get it")
        return render_template('login.html')
      except sr.RequestError:
        flash("I have a problem")
        return render_template('login.html')
    else:
      flash("incorect username or password")
      return render_template('login.html') 

ball_api = requests.get("https://www.balldontlie.io/api/v1/games")
parsed_json = json.loads(ball_api.content)
games = parsed_json['data']

@app.route('/home',methods=['GET', 'POST'])  
def home():
  if request.method == 'GET':
    return render_template('home.html')
  else:
    return render_template('home.html', games=games)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'GET':
    return render_template('signup.html')
  else:
    temp_username = request.form['username']
    temp_password = request.form['password']

    found_user = users.query.filter_by(username =temp_username).first()

    if found_user:
      flash("username is taken")
      return render_template('signup.html')
    else:
      try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
          audio = r.listen(source)
          voice_data = r.recognize_google(audio)
          usr = users(temp_username,temp_password, voice_data)
          db.session.add(usr)
          db.session.commit()
          return redirect(url_for('login'))
      except sr.UnknownValueError:
        flash("I did not get it")
        return render_template('signup.html')
      except sr.RequestError:
        flash("I have a problem")
        return render_template('signup.html')
      

@app.route('/logout')
def logout(): 
  return redirect(url_for('login'))

db.create_all()

if __name__ == "__main__":
	app.run(
		host='0.0.0.0', 
		port=5000, 
    debug=True
	)