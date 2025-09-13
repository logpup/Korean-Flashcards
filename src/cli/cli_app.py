# Python standard library imports
import argparse
import os

# Imported methods from other pages
from data_utils.data_loader import import_candidate_file
from logic.logic_processor import populate_flaschard_data
from utils.utils_export import export_flashcard_data

def cli_prompt():
    """
    Main entry point for the flashcard generator CLI.

    Example:
    python src/main.py generate <input_file> --output-dir <output_directory>
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
        help="Generate flashcard entries for a list of Korean words from an input file."
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

        # Load the data from the specified file
        word_data = import_candidate_file(args.filepath)

        # Process the data to populate flashcard information
        if not word_data.empty:
            print(f"Processing {len(word_data)} words...")
            populate_flaschard_data(word_data)
        else:
            print("No data to process. Exiting.")

        # Export the processed data to the specified output directory
        output_file = os.path.join(args.output_dir, "flashcards.txt")
        export_flashcard_data(word_data, output_file)