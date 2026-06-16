from extensions import db
from models import CaseProblem, CaseProblem_History, Problem, History

def sync_cp_history(user_id: str):

   case_problems_list = [record for record in db.session.query(CaseProblem).all()]

   user_histories = {row.problem_id:row.status for row in CaseProblem_History.query.filter(CaseProblem_History.user_id == int(user_id)).all()}   

   for case in case_problems_list:

      if case.id not in user_histories:

         new_record = CaseProblem_History(user_id = int(user_id), problem_id = case.id, difficulty = case.difficulty)

         db.session.add(new_record)
         db.session.flush()

         user_histories[case.id] = new_record.status

   db.session.commit()

   status_list = [user_histories[case.id] for case in case_problems_list]

   return status_list

def sync_op_history(user_id: str):

   problems_list = [record for record in db.session.query(Problem).all()]

   user_histories = {history.problem_id : history.status  for history in History.query.filter(History.user_id == int(user_id)).all()}

   for problem in problems_list:

      if problem.problem_id not in user_histories:

         new_record = History(user_id = int(user_id), problem_id = problem.problem_id, difficulty = problem.difficulty)

         db.session.add(new_record)

         db.session.flush()

         user_histories[problem.problem_id] = new_record.status

   db.session.commit()

   status_list = [user_histories[problem.problem_id] for problem in problems_list]

   return status_list