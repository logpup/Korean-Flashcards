#main.py
from cli.cli_app import cli_prompt
from data_utils.data_loader import run_ui # < insert method here>
from data_utils.data_cleaner import run_ui # < insert method here>
from data_utils.data_structure import run_ui # < insert method here>

def main ():
    cli_prompt()

if __name__ == "__main__":
    main()