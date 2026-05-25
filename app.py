from flask import Flask, render_template, request, redirect, session, make_response
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from admin import admin_bp
from extensions import db, engine
from flask_cors import CORS
from flask_migrate import Migrate
import os 
import subprocess
import uuid
import json

app = Flask(__name__)
CORS(app)
app.secret_key = "REDACTED"

# uncomment if you want to try docker compose

# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_HOST = os.getenv("DB_HOST", "db")

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:REDACTED@localhost/mydatabase"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db.init_app(app)

migrate = Migrate(app, db)

with app.app_context():
   from models import User, History, Problem, CaseProblem, CaseProblem_History, TestCase, Submission, Result, Administrator
   #db.drop_all() uncomment if you will now deploy the app
   # Problem.__table__.drop(db.engine)
   # Problem.__table__.create(db.engine)
   db.create_all()

app.register_blueprint(admin_bp, url_prefix='/admin')

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

def run_secure_container(image:str, docker_flags:list[str] = None ):
         
      base_command = [

         "docker", "run",
         "--rm",
         "--user", "5000:5000",
         "--network", "none",
         "--cap-drop", "ALL",
         "--tmpfs", "/app/.pytest_cache:rw,noexec,nosuid"

      ]

      if docker_flags:

         base_command.extend(docker_flags)

      base_command.append(image)

      result  = subprocess.run(

         base_command,
         capture_output=True,
         timeout=15,
         text=True

      )

      return result.stdout, result.stderr, result.returncode

@app.route('/', methods=['GET', 'POST'])
def index():

   response = make_response(render_template('/index.html'))
   response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
   response.headers['Pragma'] = 'no-cache'
   
   return response

@app.route('/register', methods=['POST', 'GET'])
def register_user():
   if request.method == 'POST':
      first_name_form = request.form['first_name']
      last_name_form = request.form['last_name']   
      username_form = request.form['username']
      password = generate_password_hash(request.form['password'], method="pbkdf2:sha256")

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
         return render_template('popup_error.html', show_popup = True, redirect_url = "/login", popup_message = "The user does not exist")
      
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
               
@app.route('/case_problems/solving-page/<int:id>/submit', methods=['POST', 'GET'])
def submit(id):

   user_code = request.form['code']

   submission_id = str(uuid.uuid4())

   base_dir = os.path.abspath("submission")

   submission_dir = os.path.join(base_dir, submission_id)

   os.makedirs(submission_dir, exist_ok=True)

   with open(os.path.join(submission_dir, "solution.py"), "w") as f:
      f.write(user_code)

   current_problem = CaseProblem.query.get(id)
   
   with engine.connect() as connection:
      table = connection.execute(text("SELECT * FROM mydatabase.test_case WHERE problem_id = :id"), {"id": id})

      connection.close()
   
   test_cases_json = json.dumps([{"input": t.input_data, "expected": t.expected_output} for t in table])

   #run a container using my docker image

   result = run_secure_container("python-test-runner:latest", docker_flags=[

   "--env", f"TEST_CASES={test_cases_json}",
   "--env", f"FUNCTION_NAME={current_problem.function_name}",
   "-v", f"{os.path.abspath(submission_dir)}:/app/submission"

   ])
                                                   


   # try:

   #    result = subprocess.run(

   #       [
   #          "docker", "run", "--rm",
   #          "-v", f"{os.path.abspath(submission_dir)}:/app/submission",
   #          "-e" f"TEST_CASES={test_cases_json}",
   #          "-e" f"FUNCTION_NAME={current_problem.function_name}", 
   #          "python-test-runner:latest"

   #       ], 
            
   #       capture_output=True, 
   #       text=True,
   #       timeout=10

   #    )

   # except subprocess.TimeoutExpired:
   #    return render_template("result.html", output="", error="Time limit exceeded!")



   return render_template("result.html", result = result)

@app.route('/output_problems', methods=['GET', 'POST'])
def output():

   user_id = session.get("user_id")

   if not user_id:
      return redirect('/login')
   
   problems_list = Problem.query.all()
  
   for problem in problems_list:

      if not History.query.filter(History.user_id == user_id).first():

         for problem in problems_list:

            history = History(problem_id=problem.problem_id, user_id=int(user_id))

            db.session.add(history)
            db.session.commit()

      elif not History.query.filter(History.problem_id == problem.problem_id).first():

         history = History(problem_id=problem.problem_id, user_id=int(user_id))

         db.session.add(history)
         db.session.commit()

   status_list = []

   for problem in problems_list:

      status_list.append(db.session.query(History.status).filter(History.user_id == user_id, History.problem_id == problem.problem_id).scalar())

   else:
       
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
