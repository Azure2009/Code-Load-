from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import make_response
import subprocess

db = SQLAlchemy()

def nocache(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated

def run_secure_container(image:str, docker_flags:list[str] = None ):
         
      base_command = [

         "docker", "run",
         "--rm",
         "--user", "5000:5000",
         "--network", "none",
         "--cap-drop", "ALL",
         "--read-only",
         "--tmpfs", "/tmp:rw,noexec,nosuid",
         "--tmpfs", "/app/.pytest_cache:rw,noexec,nosuid",

      ]

      if docker_flags:

         base_command.extend(docker_flags)

      base_command.append(image)

      try:

         result  = subprocess.run(

            base_command,
            capture_output=True,
            timeout=15,
            text=True,
            

         )

         return result.stdout, result.stderr, result.returncode
      
      except subprocess.TimeoutExpired:

         return "", "Time limit exceeded: your code ran too long.", -1
      
      except subprocess.CalledProcessError as e:
        return "", f"Container error: {e}", -1

      except Exception as e:
        return "", f"Unexpected error: {e}", -1