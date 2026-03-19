import subprocess

result = subprocess.run(

    ["pytest", "-q", "--tb=short"],
    capture_output=True,
    text=True

)

print(result.stdout)
print(result.stderr)
print(result.returncode)