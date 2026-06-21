from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, login_user, logout_user
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from admin import admin_bp
from sync import sync_cp_history, sync_op_history
from extensions import db, nocache, run_secure_container
from init_login_manager import login_manager
import re
import os 
import uuid
import json
import shutil
import ast

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(admin_bp, url_prefix='/admin')

db.init_app(app)
login_manager.init_app(app)

CORS(app)
Migrate(app, db)

with app.app_context():
   from models import User, History, Problem, CaseProblem, CaseProblem_History, TestCase, Submission, Administrator
   db.create_all()

@app.route('/', methods=['GET', 'POST'])
@nocache
def index():
   
   return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
@nocache
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
         
         return redirect(url_for('index'))

      except Exception:

         return render_template('popup_error.html', show_popup = True, redirect_url = "/login", popup_message = "There was a problem with your registration. Please try again.")

   else:
      
      return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
@nocache
def login():
   if request.method == 'POST':

      username = request.form['username']
      password = request.form['password']
      
      user = User.query.filter(username == username).first()

      if re.search(username, user.username) and check_password_hash(user.hash_password, password):

         login_user(user)

         session['user_id'] = user.id

         return redirect(url_for('dashboard'))
      
      else:

         return render_template('popup_error.html', show_popup = True, redirect_url = "/login", popup_message = "The user does not exist")
      
   else:

      return render_template('login.html')
   
@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('login'))
   
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
@nocache
def dashboard():

   user_id = session.get('user_id')

   user = User.query.get(int(user_id))
    
   sync_cp_history(user_id)

   sync_op_history(user_id)
   
   return render_template('dashboard.html', user=user)

@app.route('/dashboard/account', methods=['GET', 'POST'])
@login_required
@nocache
def user_account():

   user_id = session.get("user_id")

   user = User.query.get(user_id)
  
   total_unsolved_op = History.query.filter(History.status == "unsolved", History.user_id == int(user_id)).count()

   total_unsolved_cp = CaseProblem_History.query.filter(CaseProblem_History.status == "unsolved", CaseProblem_History.user_id == int(user_id)).count()

   solved_op_hashmap = {}
   total_op_hashmap = {}

   solved_cp_hashmap = {}
   total_cp_hashmap = {}

   difficulties = ["Easy", "Medium", "Hard"]

   for d in difficulties:

      # Get all solved and total output problems for each difficulty category
      solved_op_hashmap.setdefault(d, History.query.filter(History.status == "solved", History.difficulty == d, History.user_id == int(user_id)).count())   
      total_op_hashmap.setdefault(d, History.query.filter(History.difficulty == d, History.user_id == int(user_id)).count())

      # Get all solved and total case problems for each difficulty category
      solved_cp_hashmap.setdefault(d, CaseProblem_History.query.filter(CaseProblem_History.status == "solved", CaseProblem_History.difficulty == d, CaseProblem_History.user_id == int(user_id)).count())
      total_cp_hashmap.setdefault(d, CaseProblem_History.query.filter(CaseProblem_History.difficulty == d, CaseProblem_History.user_id == int(user_id)).count())

   return render_template(

      "user_account.html",
      user = user,
      total_unsolved_op = total_unsolved_op,
      total_unsolved_cp = total_unsolved_cp,
      solved_op_hashmap = solved_op_hashmap,
      solved_cp_hashmap = solved_cp_hashmap,
      total_op_hashmap = total_op_hashmap,
      total_cp_hashmap = total_cp_hashmap                             
   )

@app.route('/case_problems', methods=['GET', 'POST'])
@login_required
@nocache
def case():

   user_id = session["user_id"]

   if not user_id:

      redirect("/login")

   case_problems_list = CaseProblem.query.all()

   status_list = sync_cp_history(user_id)

   return render_template("case_problems.html", case_problems_list = case_problems_list, status_list = status_list)

@app.route('/case_problems/solving-page/<int:id>', methods=['GET', 'POST'])
@login_required
@nocache
def case_problem(id):

   case_problem = CaseProblem.query.get(id)
   user_id = session.get("user_id")
   fresh = request.args.get('fresh') == 'true'
    
   saved_code = None

   if not fresh:
      history = CaseProblem_History.query.filter_by(user_id=int(user_id), problem_id=id).first()
      saved_code = history.last_submission if history and history.last_submission else None

   return render_template("solving_page-case_problems.html", case_problem = case_problem, saved_code = saved_code)
               
@app.route('/case_problems/solving-page/<int:id>/submit', methods=['POST', 'GET'])
@login_required
@nocache
def submit(id):

   def safe_cast(value: str):
          
      try:

         return ast.literal_eval(value)

      except (ValueError, SyntaxError):

         return value
      
   def deserialize_input(raw: str) -> list:
    try:
        result = json.loads(raw)
        if not isinstance(result, list):
            result = [result]  # safety fallback
        return result
    except json.JSONDecodeError:
        # fallback for old bare-value rows during migration
        return [ast.literal_eval(raw)]

   user_code = request.form['code']

   submission_id = str(uuid.uuid4())

   base_dir = os.path.abspath("submission")

   submission_dir = os.path.join(base_dir, submission_id)

   current_problem = CaseProblem.query.get(id)

   try:

      os.makedirs(submission_dir, exist_ok=True)

      with open(os.path.join(submission_dir, "solution.py"), "w") as f:
         f.write(user_code)
         f.flush()
         os.fsync(f.fileno())

      history = db.session.query(CaseProblem_History).filter(
      CaseProblem_History.user_id == int(session.get("user_id")),
      CaseProblem_History.problem_id == id
      ).first()

      if history:
         history.last_submission = user_code
         db.session.commit()

      function_name = db.session.get(CaseProblem, id).function_name

      table = db.session.query(TestCase).filter(TestCase.problem_id == id).all()
      
      test_cases_list = [
         {

         "input": deserialize_input(t.input_data), 
         "expected": safe_cast(t.expected_output),
         "unordered": current_problem.unordered
          
         } for t in table]

      with open(os.path.join(submission_dir, "test_cases.json"), "w") as f:

         json.dump(test_cases_list, f)
         f.flush()
         os.fsync(f.fileno())

      HOST_SUBMISSION_BASE = os.environ.get("HOST_SUBMISSION_DIR")

      if HOST_SUBMISSION_BASE:
         host_submission_dir = os.path.join(HOST_SUBMISSION_BASE, submission_id)
      else:
         host_submission_dir = os.path.abspath(submission_dir)

      #run a container using my docker image

      stdout, stderr, exit_code = run_secure_container("python-test-runner:latest", docker_flags=[

      "--memory", "128m",
      "--memory-swap", "128m",
      "--cpus", "0.5",
      "--pids-limit", "50",
      "--stop-timeout", "10",
      "--env", f"FUNCTION_NAME={function_name}",
      "-v", f"{host_submission_dir}:/app/submission:ro",

      ])

      output = stdout + stderr

      # Check output content first, before exit_code
      if exit_code == 0:
         verdict = "Accepted"
         db.session.query(CaseProblem_History).filter(CaseProblem_History.problem_id == id).update({CaseProblem_History.status: "solved"})
         db.session.commit()

      elif exit_code == -1:
         verdict = "Time Limit Exceeded" if "Time limit exceeded" in output else "System Error"
      else:
         if "TabError" in output or "SyntaxError" in output or "IndentationError" in output:
            verdict = "Syntax Error"
         elif "NameError" in output or "TypeError" in output or "AttributeError" in output:
            verdict = "Runtime Error"
         elif "AssertionError" in output:
            verdict = "Wrong Answer"
         else:
            verdict = "Runtime Error"

   finally:

      shutil.rmtree(submission_dir, ignore_errors=True)
                                                
   return render_template("result.html", verdict = verdict, output = output, id = id)

@app.route('/output_problems', methods=['GET', 'POST'])
@login_required
@nocache
def output():

   user_id = session.get("user_id")

   if not user_id:
      return redirect('/login')
   
   problems_list = Problem.query.all()

   status_list = sync_op_history(user_id)

   return render_template("output_problems.html", status_list=status_list, problems_list=problems_list)

@app.route('/output_problems/solving_page/<int:problem_id>', methods=['POST', 'GET'])
@login_required
@nocache
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

            flash('Accepted', 'accepted')

         else:

            flash('Wrong Answer', 'wrong')

         return redirect('/output_problems')
            
      problem = Problem.query.get_or_404(problem_id)

      return render_template("solving_page-output_problems.html", problem=problem)
   
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)
