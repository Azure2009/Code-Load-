from flask import request, session, render_template, redirect, url_for, jsonify
from flask_login import logout_user, login_user, login_required
from werkzeug.security import check_password_hash
from models import Administrator, Problem, CaseProblem, TestCase, History, CaseProblem_History
from extensions import nocache
from extensions import db
from admin import admin_bp
from trie_data_structure import trie
import json, ast

trie_obj = trie()
trie_obj_2 = trie()


@admin_bp.route('/', methods=['POST', 'GET'])
@nocache
def administrator():

   if request.method == 'POST':

      username = request.form['username']

      password = request.form['password']

      admin = Administrator.query.filter_by(username = username).first()     

      if admin and check_password_hash(admin.password, password):
         
         session["admin_id"] = admin.id

         login_user(admin)

         return redirect(url_for('admin.adminDashboard'))
      
      else: 

         return render_template("admin/popup.html", show_popup = True, redirect_url = "/admin", popup_message = "The admin does not exist")
         
   return render_template("admin/login.html")

@admin_bp.route('/logout')
@login_required
def admin_logout():

   logout_user()
   return redirect(url_for('admin.administrator'))

@admin_bp.route('/dashboard', methods=['POST', 'GET'])
@nocache
@login_required
def adminDashboard():

   id = session.get("admin_id")

   current_admin = Administrator.query.get_or_404(id)

   if not id:

      return redirect("/admin/")
   
   return render_template("admin/dashboard.html", admin = current_admin)

@admin_bp.route('/dashboard/new_output_problem', methods=['POST', 'GET'])
@nocache
@login_required
def outputProblem_creation():

   titles = [row[0] for row in db.session.query(Problem.problem_title).all()] 

   for title in titles:

      trie_obj_2.insert(title)

   if request.method == 'POST':

      problem_title = request.form["problem_title"]

      problem_description = request.form["problem_description"]

      coding_problem = request.form["coding_problem"]

      expected_output = request.form["expected_output"]

      difficulty = request.form.get('difficulty')

      try:

         converted = bool(difficulty)

         assert True == converted

         new_output_problem = Problem(problem_title = problem_title, problem_description = problem_description,problem_set = coding_problem, expected_output = expected_output, difficulty = difficulty)

         db.session.add(new_output_problem)
         db.session.commit()

         trie_obj_2.insert(new_output_problem.problem_title)

      except AssertionError:

         return render_template('admin/popup.html', show_popup = True, redirect_url = '/admin/dashboard/new_output_problem', popup_message = "A difficulty must be selected.")

      except Exception as e:

         return render_template('admin/popup.html', show_popup = True, redirect_url = '/admin/dashboard/new_output_problem', popup_message = f"{e}")

   return render_template('admin/output_problem_creation.html')

@admin_bp.route('/dashboard/new_output_problem/search', methods=['POST', 'GET'])
@nocache
@login_required
def search_handler():

   query = request.args.get('q', '')

   matching_titles = trie_obj_2.getWordsWithPrefix(query)

   results = []

   for title in matching_titles:

      problem = db.session.query(Problem.problem_id, Problem.problem_title).filter(Problem.problem_title == title).first()

      if problem:

         results.append({'id': problem[0], 'title':problem[1]})

   return jsonify(results)

@admin_bp.route('/dashboard/new_output_problem/delete/<id>', methods=['POST', 'GET'])
@nocache
@login_required
def delete_output_problem(id):

   parsed_id = str(id)

   try:

      record = db.session.query(Problem).filter(Problem.problem_id == int(parsed_id)).first()

      if not record:
         raise Exception("Problem not found")

      histories = db.session.query(History).filter(History.problem_id == int(parsed_id)).all()

      for history in histories:
         db.session.delete(history)

      db.session.delete(record)

      db.session.commit()

      return redirect('/admin/dashboard/new_output_problem')

   except Exception:

      return render_template("admin/popup.html", show_popup=True, popup_message="A problem from search results must be selected.", redirect_url="/admin/dashboard/new_output_problem")


@admin_bp.route('/dashboard/new_case_problem', methods= ['POST', 'GET'])
@nocache
@login_required
def case_problem_creation():

   if request.method == "POST":

      problem_title = request.form['problem_title']
      coding_problem = request.form['coding_problem']
      examples = request.form['examples']
      constraints = request.form['constraints']
      follow_ups = request.form['follow_ups']
      hints = request.form['hints']
      difficulty = request.form.get('difficulty')
      function_name = request.form['function_name']
      args = request.form['args']
      return_type = request.form['return_type']
      

      if request.form['follow_ups'] == "":

         follow_ups = None

      if request.form['hints'] == "":

         hints = None
   
      unordered = 'unordered' in request.form

      try:

         converted = bool(difficulty)

         assert True == converted 

         new_case_problem = CaseProblem(

         title = problem_title, 
         instruction = coding_problem, 
         example = examples, 
         constraints = constraints, 
         follow_up = follow_ups, 
         hint = hints,
         difficulty = difficulty,
         function_name = function_name,
         args = args,
         return_type = return_type,
         unordered = unordered
         
         )

         db.session.add(new_case_problem)
         db.session.commit()

      except AssertionError:

         return render_template("admin/popup.html", show_popup = True, popup_message = "A difficulty must be selected.", redirect_url = "/admin/dashboard/new_case_problem")

      except Exception as e:

         return render_template("admin/popup.html", show_popup = True, popup_message = f"{e}", redirect_url = "/admin/dashboard/new_case_problem")

   return render_template('admin/case_problem_creation.html')
 
@admin_bp.route('/dashboard/new_test_case', methods= ['POST', 'GET'])
@nocache
@login_required
def test_case_creation():
      
      def split_top_level(s: str) -> list[str]:
         
         args = []
         depth = 0
         current = []
         for ch in s:
            if ch in '([{':
                  depth += 1
            elif ch in ')]}':
                  depth -= 1
            if ch == ',' and depth == 0:
                  args.append(''.join(current))
                  current = []
            else:
                  current.append(ch)
         if current:
            args.append(''.join(current))
         return args
   
      def parse_input_line_to_json(line: str) -> str:
         
         # Split by top-level commas only (not commas inside brackets)
         args = split_top_level(line)
         parsed_args = [ast.literal_eval(arg.strip()) for arg in args]
         return json.dumps(parsed_args)

      # insert all case problem titles in trie object

      case_problem_titles = [row[0] for row in db.session.query(CaseProblem.title).all()]
   
      for title in case_problem_titles:

         trie_obj.insert(title)

      if request.method == "POST":

         new_testCases = request.form["new_TestCases"]

         new_expected_output = request.form["new_expected_output"]

         problem_id_raw = request.form.get('problem_id')

         if not problem_id_raw:

            return 'Please select a problem first'
         
         problem_id = int(problem_id_raw)

         lines_testCases = [line.strip() for line in new_testCases.splitlines() if line.strip()]

         lines_expected_output = [line.strip() for line in new_expected_output.splitlines() if line.strip()]

         #insert every submitted test case and expected output to its designated problem record
         try:

            for test_case, expected_output in zip(lines_testCases, lines_expected_output):

               serialized_input = parse_input_line_to_json(test_case)

               tc = TestCase(problem_id = problem_id, input_data = serialized_input, expected_output = expected_output)

               db.session.add(tc)

            db.session.commit()

         except Exception as e:

            db.session.rollback()
            print(f"Error: {e}")
            return f"There was a problem: {e}"

      return render_template('admin/test_case_creation.html')

@admin_bp.route('/dashboard/new_test_case/delete/<id>', methods=['POST', 'GET'])
@nocache
@login_required
def test_case_deletion(id):
   parsed_id = str(id)
   try:
      record = db.session.query(CaseProblem).filter(CaseProblem.id == int(parsed_id)).first()
      if not record:
         raise Exception("Problem not found")
      histories = db.session.query(CaseProblem_History).filter(CaseProblem_History.problem_id == int(parsed_id)).all()
      test_cases = db.session.query(TestCase).filter(TestCase.problem_id == int(parsed_id)).all()
      for history in histories:
         db.session.delete(history)
      for test_case in test_cases:
         db.session.delete(test_case)
      db.session.delete(record)
      db.session.commit()
      return redirect('/admin/dashboard/new_test_case')
   except Exception:
      return render_template("admin/popup.html", show_popup=True, popup_message="A problem from search results must be selected.", redirect_url="/admin/dashboard/new_test_case")

@admin_bp.route('/dashboard/new_test_case/query', methods= ['GET'])
@nocache
@login_required
def query_handler():

   query = request.args.get('q', '')

   matching_titles = trie_obj.getWordsWithPrefix(query)

   results = []

   for title in matching_titles:

      problem = db.session.query(CaseProblem.id, CaseProblem.title).filter(CaseProblem.title == title).first()

      if problem:

         results.append({'id': problem[0], 'title':problem[1]})

   return jsonify(results)
