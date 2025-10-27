from dotenv import load_dotenv
import os

def load_environment_variables():
    """
    Load environment variables from a .env file located in the project root.
    This function should be called at the very start of your application.
    """
    # 1. Load the environment variables from the .env file
    # This must be the very first thing you do in your script.
    load_dotenv()

    # 2. Access the variables securely using os.environ.get()
    db_name = os.environ.get("MONGO_DB_NAME")
    krdict_key = os.environ.get("KRDICT_KEY")
    python_path = os.environ.get("PYTHONPATH")

    # 3. Your application logic
    print(f"Loaded DB Name: {db_name}")
    print(f"Loaded KRDict Key (first 4 chars): {krdict_key[:4]}...")

    # Example: Ensure PYTHONPATH is set if you need it at runtime
    # (Though PYTHONPATH is typically needed by the shell, not Python itself)
    # This check is often omitted since venv/Python already handle paths well.
    if python_path == "src":
        print("PYTHONPATH is correctly set to 'src'.")