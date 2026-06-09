import subprocess, sys

result = subprocess.run(

    ["pytest", "-v", "--tb=short"],
    capture_output=True,
    text=True

)

print(result.stdout)
print(result.stderr)

sys.exit(result.returncode) 