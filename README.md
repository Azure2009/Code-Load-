## Live Demo
http://178.128.214.173:5000

# CodeLoad

A LeetCode-style online judge platform with a minimalist design built with Flask, Docker, and MySQL. 

Python is the most in demand language right now. Whether you are an experienced python programmer or just starting out, you can use this to keep your coding fundamentals intact in the AI era!

## Features
- Secure sandboxed code execution using Docker (memory limits, CPU limits, PID caps, no network access)
- Multi-argument test case support with dynamic type casting
- Dual authentication system (User and Administrator)
- Trie data structure-powered problem search
- Admin dashboard for creating problems and test cases


## Tech Stack
Flask, SQLAlchemy, Flask-Login, Flask-Migrate, Docker, MySQL, pytest, HTML, Jinja, CSS

## Screenshots

![Dashboard](docs/images/CodeLoad/Main_Dashboard.png)
![Sample Problem](docs/images/CodeLoad/Sample_Case_Problem.png)
![Sample Passed Verdict](docs/images/CodeLoad/Sample_Correct_Verdict.png)
![Sample Wrong Answer Verdict](docs/images/CodeLoad/Sample_Wrong_Answer_Verdict.png)
![Sample Runtime Error Verdict](docs/images/CodeLoad/Sample_Runtime_Error_Verdict.png)
![Sample Problems](docs/images/CodeLoad/Case_Problems.png)

## Local Setup
1. Clone the repo
2. Create a `.env` file (see `.env.example`)
3. `docker compose up -d --build`
4. `docker compose exec backend flask db upgrade`
5. `docker compose exec backend python seed_admin.py`

## Known Limitation

**Supports:**

1. built-in Python data types (`int`, `float`, `str`, `bool`, `list`, `dict`, `tuple`, etc.) for test case inputs and outputs to keep the system general-purpose.

2. Unordered output comparison


**Not supported (YET):**

1. Problems that require deserializing inputs into custom objects (e.g. linked lists, binary trees)
2. In-place mutation / custom judge problems
3. No return values problems
4. Coding challenges not written in python.
