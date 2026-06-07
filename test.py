from models import CaseProblem

#list[list[list[str]]]
# import ast

# new_list = '[[["a", "a", "a", "a"], ["b", "b"]], ["c", "c"]]'

# primitiveType_map = {

#       "int": int, 
#       "bool": bool,
#       "float": float,
#       "str": str
       
#    }

# def _deepCheck_list(my_list:str = None):

#       literal_list = ast.literal_eval(my_list)

#       if not literal_list:
#         return "" 
      
#       if isinstance(literal_list[0], list):
         
#          return f"list[{_deepCheck_list(f"{literal_list[0]}")}]"
            
#       for key in primitiveType_map:

#          if primitiveType_map[key] is not None:

#             if isinstance(literal_list[0], primitiveType_map[key]):
               
#                return key 
            
#       return ""


def safe_cast(value: str, id: int):

      primitiveType_map = {

      "int": int, 
      "bool": bool,
      "float": float,
      "str": str
       
   }

      problem = CaseProblem.query.get(id)

      arguments = str(problem.args).split(',')

      for arg in arguments:

         splitted_parameter = arg.split(':')

         for key in primitiveType_map:

            if splitted_parameter[1].strip() == key:

               return primitiveType_map[key](value)
            
safe_cast("42", 3)
            

