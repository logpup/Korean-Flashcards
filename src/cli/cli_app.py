import argparse
import os

# Assume these functions are defined in your project's logic and data_utils modules.
# We'll import them here to demonstrate the full application flow.
# If these files are nested in a 'src' directory, the import would be 'from src.logic.logic_processor import ...'
# and 'from src.data_utils.data_loader import ...'
from data_utils.data_loader import import_candidate_file
from logic.logic_processor import populate_flaschard_data


def cli_prompt():
    """
    Main entry point for the flashcard generator CLI.
    """
    # 1. Create the top-level parser
    parser = argparse.ArgumentParser(
        description="A CLI tool to generate flashcards from a list of Korean words.",
        epilog="Example: python main.py generate data/words.csv --output-dir flashcards"
    )

    # 2. Add sub-commands for different actions
    # 'generate' will be a positional argument
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # 3. Create a parser for the "generate" command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate flashcards (images and audio) from an input file."
    )
    generate_parser.add_argument(
        "filepath",
        type=str,
        help="Path to the input file (e.g., .csv, .txt)."
    )
    generate_parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="flashcards",
        help="Directory to save the generated flashcards."
    )

    # 4. Parse the arguments
    args = parser.parse_args()

    # 5. Handle the command based on the parsed arguments
    if args.command == "generate":
        print(f"Starting flashcard generation from file: {args.filepath}")
        
        # Check if the file exists before proceeding
        if not os.path.exists(args.filepath):
            print(f"Error: The file '{args.filepath}' does not exist.")
            return

        # Load the data using a function from your data_utils module
        word_data = import_candidate_file(args.filepath)

        if not word_data.empty:
            # Process the flashcards using a function from your logic module
            populate_flaschard_data(word_data, args.output_dir) # HERE !!!
            print("🎉 Flashcard generation completed!")
        else:
            print("No data to process. Exiting.")