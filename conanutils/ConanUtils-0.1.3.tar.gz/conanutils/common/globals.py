import os
import sys

conan_profile_path = ""
python_exe = ""
conan_exe = ""
conan_user_path = ""


def compute_globals():
    global conan_profile_path
    global python_exe
    global conan_exe
    global conan_user_path

    if os.getenv('PYTHON_EXE'):
        python_exe = os.getenv('PYTHON_EXE')
    else:
        python_exe = sys.executable

    if os.getenv('CONAN_EXE'):
        conan_exe = os.getenv('CONAN_EXE')
    else:
        conan_exe = "conan"

    # get conan user home
    if os.getenv("CONAN_USER_HOME"):
        conan_user_path = os.path.join(os.environ['CONAN_USER_HOME'], ".conan")
    else:
        conan_user_path = os.path.join(os.path.expanduser("~"), ".conan")

    print("python executable: ", python_exe)
    print("conan executable: ", conan_exe)
    print("conan user home: ", conan_user_path)

    conan_profile_path = os.path.join(conan_user_path, "profiles")