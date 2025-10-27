#Imported modules from other files
from config.env_loader import load_environment_variables
from cli.cli_app import app

def main():
    load_environment_variables()
    app()

# This is the main entry point of the application
if __name__ == "__main__":
    main()