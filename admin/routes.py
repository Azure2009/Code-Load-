from flask import request, session, render_template, redirect, url_for, jsonify
from werkzeug.security import check_password_hash
from models import Administrator, Problem, CaseProblem,tz_utc8
from functools import wraps
from flask import make_response
from datetime import datetime
from extensions import db
from admin import admin_bp
from trie_data_structure import trie, TrieNode

trie_obj = trie()

# My decorator for security
def login_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):

      if not session.get('admin_id'):

         return redirect('/admin/')

      response = make_response(f(*args, **kwargs))
      
      response.headers['Cache-Control'] = 'no-store, no-cache, make-revalidate'
      response.headers['Pragma'] = 'no-cache'

      return response
   
   return decorated

@admin_bp.route('/', methods=['POST', 'GET'])
def administrator():

   if request.method == 'POST':

      username = request.form['username']

      password = request.form['password']

      admin = Administrator.query.filter_by(admin_username = username).first()     

      if admin and check_password_hash(admin.admin_password, password):
         
         session["admin_id"] = admin.admin_id

         return redirect('/admin/dashboard')
      
      else: 

         return render_template("admin/popup.html", show_popup = True, redirect_url = "/admin", popup_message = "The admin does not exist")
         
   else:

      return render_template("admin/login.html")

@admin_bp.route('/dashboard', methods=['POST', 'GET'])
@login_required
def adminDashboard():

   id = session.get("admin_id")

   current_admin = Administrator.query.get_or_404(id)

   if not id:

      return redirect("/admin/")
   
   return render_template("admin/dashboard.html", admin = current_admin)

@admin_bp.route('/dashboard/new_output_problem', methods=['POST', 'GET'])
@login_required
def outputProblem_creation():

   session['visited_at'] = datetime.now(tz_utc8).isoformat()
   
   if request.method == 'POST':

      problem_title = request.form["problem_title"]

      coding_problem = request.form["coding_problem"]

      expected_output = request.form["expected_output"]

      difficulty = request.form.get('difficulty')

      if difficulty == "":

         return render_template('admin/popup.html', show_popup = True, redirect_url = '/admin/dashboard/new_output_problem', popup_message = "A difficulty must be selected.")
         
      else: 

         new_output_problem = Problem(problem_title = problem_title, problem_set = coding_problem, expected_output = expected_output, difficulty = difficulty)

         db.session.add(new_output_problem)
         db.session.commit()

   return render_template('admin/output_problem_creation.html')

@admin_bp.route('/dashboard/new_case_problem', methods= ['POST', 'GET'])
@login_required
def case_problem_creation():

   return render_template('admin/case_problem_creation.html')
 
@admin_bp.route('/dashboard/new_test_case', methods= ['POST', 'GET'])
@login_required
def test_case_creation():

   outputProblem_titles = [row[0] for row in db.session.query(Problem.problem_title).all()]

   for title in outputProblem_titles:
      
      trie_obj.insert(title)

   if request.method == 'POST':

      new_testCases = request.form.get('new_TestCases', '')

      lines_testCases = [line.strip() for line in new_testCases.splitlines() if line.strip()]

   return render_template('admin/test_case_creation.html')

@admin_bp.route('/dashboard/new_test_case/query', methods= ['GET'])
def query_handler():

   query = request.args.get('q', '')

   response = trie_obj.getWordsWithPrefix(query)

   return jsonify(response)