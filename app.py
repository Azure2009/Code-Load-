from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash 
import pymysql

app = Flask(__name__)

app.secret_key = "0920juancarlo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0920juancarlo@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

conn = pymysql.connect(

   host="localhost",
   user="root",
   password="0920juancarlo",
   database="mydatabase",
   cursorclass=pymysql.cursors.DictCursor

)

cursor = conn.cursor()

db = SQLAlchemy(app)

class User(db.Model):
   user_id = db.Column(db.Integer, nullable = False, primary_key=True)
   first_name = db.Column(db.String(200), nullable = False)
   last_name = db.Column(db.String(200), nullable = False)   
   username = db.Column(db.String(200), nullable = False, unique= True)
   hash_password = db.Column(db.String(200), nullable = False)
   
class Problem(db.Model):
   problem_id = db.Column(db.Integer, nullable = False, primary_key=True)
   problem_title = db.Column(db.String(200), nullable = False)
   problem_set = db.Column(db.Text, nullable = False)
   expected_output = db.Column(db.Text, nullable = False)
   difficulty = db.Column(db.String(50), nullable = False)

class TestCase(db.Model):
   test_case_id = db.Column(db.Integer, nullable = False, primary_key=True)
   test_case = db.Column(db.Text, nullable = False)

class Submission(db.Model):
   submission_id = db.Column(db.Integer, nullable = False, primary_key=True)
   submission = db.Column(db.Text, nullable = False)
   user_id = db.Column(db.Integer, nullable = False)


class Result(db.Model):
   result_id = db.Column(db.Integer, nullable = False, primary_key=True)
   result = db.Column(db.String(50), nullable = False)
   submission_id = db.Column(db.Integer, nullable = True)
   

with app.app_context():
   db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
   return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register_user():
   if request.method == 'POST':
      first_name_form = request.form['first_name']
      last_name_form = request.form['last_name']   
      username_form = request.form['username']
      password = generate_password_hash(request.form['password'])

      registeredUser = User(first_name = first_name_form, last_name = last_name_form, username = username_form, hash_password = password)

      try:

         db.session.add(registeredUser)
         db.session.commit()
         
         return redirect('/')

      except:
         return 'There was a problem in your registration'

   else:
      return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
   if request.method == 'POST':

      username = request.form['username']
      password = request.form['password']

      user = User.query.filter_by(username=username).first()

      if user and check_password_hash(user.hash_password, password):

         session.clear()

         session["user_id"] = user.user_id

         return redirect(url_for("dashboard"))
      
      else:
         return render_template('login.html')
      
   else:
      return render_template('login.html')
   
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
   user_id = session.get("user_id")
  
   if not user_id:
      return redirect('/login')
   
   current_user = User.query.get_or_404(int(user_id))

   problems_list = Problem.query.all()

   return render_template("dashboard.html", current_user=current_user, problems_list=problems_list) 

@app.route('/solving_page/<int:problem_id>', methods=['POST', 'GET'])
def problem(problem_id):

      problem = Problem.query.get_or_404(problem_id)

      return render_template("solving_page.html", problem=problem)
   
@app.route('/solving_page/submit', methods=['POST', 'GET'])
def submit():

   if request.method == 'POST':


      submission_form = request.form["submission"]

      user_submission = Submission(submission = submission_form)
   
      try:

         db.session.add(user_submission)
         db.session.commit()

      except:
         return redirect('/dashboard')


   else:
      return redirect('/dashboard')

if __name__ == '__main__':
   app.run(debug=True)
