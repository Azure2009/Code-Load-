from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
import time
import os 
import subprocess
import uuid

app = Flask(__name__)
app.secret_key = "REDACTED"


# uncomment if you want to try docker compose

# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_HOST = os.getenv("DB_HOST", "db")

app.config['SQLALCHEMY_DATABASE_URI'] = (
   
   "mysql+pymysql://root:REDACTED@localhost/mydatabase"


)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# def wait_for_db():
#    while True:
#       try:
#          with app.app_context():
#             db.engine.connect()
#             print("Database ready")
#          break
#       except Exception as e:
#             print("Waiting for database...")
#             time.sleep(3)

# wait_for_db()


class User(db.Model):
   user_id = db.Column(db.Integer, nullable = False, primary_key=True)
   first_name = db.Column(db.String(200), nullable = False)
   last_name = db.Column(db.String(200), nullable = False)   
   username = db.Column(db.String(200), nullable = False, unique= True)
   hash_password = db.Column(db.String(200), nullable = False)

class History(db.Model):
   history_id = db.Column(db.Integer, nullable=False, primary_key=True)
   user_id = db.Column(db.Integer, nullable=False)
   problem_id = db.Column(db.Integer, nullable=False)
   status = db.Column(db.String(50), nullable=False, default="unsolved")

class Problem(db.Model):
   problem_id = db.Column(db.Integer, nullable = False, primary_key=True)
   problem_title = db.Column(db.String(200), nullable = False)
   problem_set = db.Column(db.Text, nullable = False)
   expected_output = db.Column(db.Text, nullable = False)
   difficulty = db.Column(db.String(50), nullable = False)

class CaseProblem(db.Model):
   id = db.Column(db.Integer, nullable = False, primary_key=True)
   title = db.Column(db.String(200), nullable = False)
   instruction = db.Column(db.Text, nullable = False)
   example = db.Column(db.Text, nullable = False)
   constraints = db.Column(db.Text, nullable = False)
   follow_up = db.Column(db.Text, nullable = True)
   hint = db.Column(db.Text, nullable = True)
   difficulty = db.Column(db.String(200), nullable = False)
   function_name = db.Column(db.String(200), nullable = False)
   
class CaseProblem_History(db.Model):
   id = db.Column(db.Integer, nullable = False, primary_key=True)
   user_id = db.Column(db.Integer, nullable=False)
   problem_id = db.Column(db.Integer, nullable=False)
   status = db.Column(db.String(50), nullable=False, default="unsolved")

class TestCase(db.Model):
   test_case_id = db.Column(db.Integer, nullable = False, primary_key=True)
   problem_id   = db.Column(db.Integer, nullable=False)
   input_data   = db.Column(db.Text, nullable=False)      
   expected_output = db.Column(db.Text, nullable=False)  
   
class Submission(db.Model):
   submission_id = db.Column(db.Integer, nullable = False, primary_key=True)
   submission = db.Column(db.Text, nullable = False)
   user_id = db.Column(db.Integer, nullable = False)


class Result(db.Model):
   result_id = db.Column(db.Integer, nullable = False, primary_key=True)
   result = db.Column(db.String(50), nullable = False)
   submission_id = db.Column(db.Integer, nullable = False)
   
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

         session["user_id"] = user.user_id

         return redirect('/dashboard')
      
      else:
         return render_template('login.html')
      
      
      
   else:
      return render_template('login.html')
   
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
   user_id = session.get("user_id")

   user = User.query.get(user_id)
  
   if not user_id:
      return redirect('/login')
   
   return render_template('dashboard.html', user=user)

@app.route('/case_problems', methods=['GET', 'POST'])
def case():

   case_problems_list = CaseProblem.query.all()

   return render_template("case_problems.html", case_problems_list = case_problems_list)

@app.route('/case_problems/solving-page/<int:id>', methods=['GET', 'POST'])
def case_problem(id):

   current_case_problem = CaseProblem.query.get(id) 

   return render_template("solving_page-case_problems.html", case_problem = current_case_problem)
               
@app.route('/case_problems/solving-page/<int:id>/submit', methods=['POST'])
def submit(id):

   user_code = request.form['code']

   submission_id = str(uuid.uuid4())

   base_dir = os.path.abspath("submission")

   submission_dir = os.path.join(base_dir, submission_id)

   os.makedirs(submission_dir, exist_ok=True)

   with open(os.path.join(submission_dir, "test_user.py"), "w") as f:
      f.write(user_code)

   open(os.path.join(submission_dir, "__init__.py"), "w").close()

   #run a container using your docker image
   #use the current case problem
   
   current_case_problem = CaseProblem.query.get(id) 

   try:

      result = subprocess.run(

         [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(submission_dir)}:/app/submission",
            "-e" f"EXPECTED_OUTPUT={current_case_problem.expected_output}", 
            "python-test-runner-v2"

         ], 
               
         capture_output=True, 
         text=True,
         timeout=10

      )

   except subprocess.TimeoutExpired:
      return render_template("result.html", output="", error="Time limit exceeded!")



   return render_template("result.html", output=result.stdout, error=result.stderr)

@app.route('/output_problems', methods=['GET', 'POST'])
def output():

   user_id = session.get("user_id")
  
   if not user_id:
      return redirect('/login')
   
   problems_list = Problem.query.all()

   if not History.query.filter(History.user_id == user_id).first():

      for problem in problems_list:

         history = History(problem_id=problem.problem_id, user_id=int(user_id))

         db.session.add(history)
         db.session.commit()

   status_list = []

   for problem in problems_list:

      status_list.append(db.session.query(History.status).filter(History.user_id == user_id, History.problem_id == problem.problem_id).scalar())

   return render_template("output_problems.html", status_list=status_list, problems_list=problems_list)

@app.route('/output_problems/solving_page/<int:problem_id>', methods=['POST', 'GET'])
def problem(problem_id):

      if request.method == 'POST':

         submission_form = request.form['submission']

         user_id = session.get("user_id")

         user_submission = Submission(submission = submission_form, user_id = int(user_id))

         problem = Problem.query.get_or_404(problem_id)

         history = History.query.filter(History.user_id == user_id, History.problem_id == problem.problem_id).first()

         try:

            db.session.add(user_submission)
            db.session.commit()


         except:

            return 'There was a problem submitting your answer.'
         
         if problem.expected_output == submission_form:

            history.status = "solved"

            db.session.commit()

            return redirect('/output_problems')
            
         


      problem = Problem.query.get_or_404(problem_id)

      return render_template("solving_page-output_problems.html", problem=problem)
   
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)
