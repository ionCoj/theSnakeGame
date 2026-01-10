from flask import Flask, redirect, url_for, render_template, request, make_response, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField
from wtforms import DecimalField, RadioField, SelectField, TextAreaField, FileField
from wtforms.validators import InputRequired
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import os

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
class User(db.Model, UserMixin):
  __tablename__ = "users"
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
  password: Mapped[str] = mapped_column(String(200), nullable=False)
  score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  currentGameScore: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

class RegisterForm(FlaskForm, UserMixin):
  username = StringField('username', validators=[InputRequired()])
  password = PasswordField('password', validators=[InputRequired()])

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_pyfile('config.py')
 
  db.init_app(app)
  with app.app_context():
        db.create_all()

  @app.before_request
  def WriteReguestInfoToLog():
      print("------Info-------")
      print(f"User IP: {request.remote_addr}")
      print(f"Method: {request.method}")
      print(f"Path: {request.path}")

  @app.before_request
  def CheckUserLogedIn():
    #  publicRoutes = ['register', 'login', 'static']
    #  if 'user_id' not in request.cookies and request.endpoint not in publicRoutes:
    #       return redirect(url_for('register'))
     print(f"Incoming request: {request.method} {request.url}")
     
  @app.after_request
  def ResponseInfoLogger(response):
      print("------Response After Info-------")
      print(f"Status Code: {response.status}")
      print(f"Content Type: {response.content_type}")
      return response
  
  @login_manager.user_loader
  def load_user(user_id):
      return db.session.get(User, int(user_id))
  
  @app.route('/', methods=['GET', 'POST'])
  def LogInOrRegister():
      print("why am I here")
      return redirect(url_for('register'))
  
  @app.route('/register', methods=['GET', 'POST'])
  def register():
      print("Register route accessed")
      form = RegisterForm()
      if form.validate_on_submit():
          new_user = User(
          username = form.username.data,
          password = form.password.data,
          score = 0,
          currentGameScore = 0
          )
          userExists = db.session.execute(db.select(User).filter_by(username=form.username.data)).scalar_one_or_none()
          if userExists:
              flash('Username already exists. Please choose a different one.')  
          elif form.password.data == "":
              flash('Password cannot be empty.')
          else:
              db.session.add(new_user)
              db.session.commit()
              CreateCookiesForUser(new_user)
              print(f"Registered new user: {new_user.username}")
              return redirect(url_for('playgame'))
              
      return render_template('signup.html', form=form)
  
  @app.route('/login', methods=['GET', 'POST'])
  def login():
      form = RegisterForm()
      if form.validate_on_submit():
          user = db.session.execute(db.select(User).filter_by(username=form.username.data)).scalar_one_or_none()
          if user and user.password == form.password.data:
              return CreateCookiesForUser(user)
          else:
              flash('Invalid username or password.')
      return render_template('login.html', form=form)
  
  @app.route('/playgame', methods=['GET', 'POST'])
  @login_required
  def playgame():
      return render_template('index.html')

  @app.route('/logout')
  @login_required  
  def logout():
      logout_user()
      flash('You have been logged out.')
      return redirect(url_for('login'))
  
  @app.route('/validatescore', methods=['POST'])
  @login_required
  def validatescore():
      if "tempScore" not in session:
          session["tempScore"] = 0
      session["tempScore"] += 1
      return {'status': 'success', 'tempScore': session["tempScore"]}
  
  
  @app.route('/updatescore', methods=['POST'])
  @login_required
  def updatescore():
      newScore = session.get("tempScore", 0)
      oldScore = current_user.currentGameScore
      if newScore > oldScore:
          user = db.session.get(User, current_user.id)
          user.score = newScore
          db.session.commit()
      session["tempScore"] = 0
      return {'status': 'success', 'theScore': newScore}
  
  @app.route('/getusersscores')
  def getusersscores():
      users = db.session.execute(db.select(User).order_by(User.score.desc())).scalars().all()
      scoresList = [{'player': user.username, 'score': user.score} for user in users]
      return scoresList
  
  @app.route('/leaderboard')
  def leaderboard():
      return render_template('leaderboard.html')

  return app

def CreateCookiesForUser(user):
    login_user(user)
    print(f"User {user.username} logged in successfully.")
    return redirect(url_for('playgame'))
    
if __name__ == "__main__":
  login_manager = LoginManager()
  app = create_app()
  login_manager.init_app(app)
  login_manager.login_view = 'login'
  app.run(debug=True)