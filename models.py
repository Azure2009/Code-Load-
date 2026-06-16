from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
   id = db.Column(db.Integer, nullable = False, primary_key=True)
   first_name = db.Column(db.String(200), nullable = False)
   last_name = db.Column(db.String(200), nullable = False)   
   username = db.Column(db.String(200), nullable = False, unique= True)
   hash_password = db.Column(db.String(200), nullable = False)

   def get_id(self):
      return f"user-{self.id}"

class History(db.Model):
   history_id = db.Column(db.Integer, nullable=False, primary_key=True)
   user_id = db.Column(db.Integer, nullable=False)
   problem_id = db.Column(db.Integer, nullable=False)
   status = db.Column(db.String(50), nullable=False, default="unsolved")
   difficulty = db.Column(db.String(50), nullable=False)

class Problem(db.Model):
   problem_id = db.Column(db.Integer, primary_key=True)
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
   args = db.Column(db.Text, nullable = False)
   return_type = db.Column(db.String(200), nullable = False)
   
class CaseProblem_History(db.Model):
   id = db.Column(db.Integer, nullable = False, primary_key=True)
   user_id = db.Column(db.Integer, nullable=False)
   problem_id = db.Column(db.Integer, nullable=False)
   status = db.Column(db.String(50), nullable=False, default="unsolved")
   difficulty = db.Column(db.String(50), nullable=False)

class TestCase(db.Model):
   test_case_id = db.Column(db.Integer, nullable = False, primary_key=True)
   problem_id   = db.Column(db.Integer, nullable=False)
   input_data   = db.Column(db.Text, nullable=False)      
   expected_output = db.Column(db.Text, nullable=False)  
   
class Submission(db.Model):
   submission_id = db.Column(db.Integer, nullable = False, primary_key=True)
   submission = db.Column(db.Text, nullable = False)
   user_id = db.Column(db.Integer, nullable = False)

class Administrator(db.Model, UserMixin):
   id = db.Column(db.Integer, nullable = False, primary_key=True)
   username = db.Column(db.Text, nullable = False)
   password = db.Column(db.Text, nullable = False)

   def get_id(self):
      return f"admin-{self.id}"





