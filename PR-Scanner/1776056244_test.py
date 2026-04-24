# ❌ BAD PRACTICES (should trigger warnings)

import os
import subprocess
import pickle

# ❌ Hardcoded secret
API_KEY = "12345-SECRET-KEY"

# ❌ Command Injection
def run_command(user_input):
    os.system(f"ls {user_input}")   # dangerous

# ❌ Unsafe deserialization
def load_data():
    data = b"cos\nsystem\n(S'echo hacked'\ntR."
    pickle.loads(data)

# ❌ Using eval
def calculate(expr):
    return eval(expr)

# ❌ Debug mode ON (for web apps)
DEBUG = True

if __name__ == "__main__":
    run_command("; rm -rf /")   # dangerous example
    print(calculate("2+2"))