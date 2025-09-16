# Python standard library imports
import argparse
import os

# Imported methods from other pages
from db.connection import setup_database
from data_utils.data_loader import import_candidate_file
from logic.logic_processor import populate_flaschard_data
from utils.utils_export import export_flashcard_data
from scraping.scraping_naver_dict import scrape_naver_dict

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
    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape websites for data concering the Korean words provided in a list from an input file."
    )
    scrape_parser.add_argument(
        "filepath",
        type=str,
        help="Path to the input file (e.g., .csv, .txt)."
    )

    # 4. Parse the arguments
    args = parser.parse_args()

    # 5. Handle the command based on the parsed arguments
    if args.command == "scrape":

        print(f"Starting to scrape data online for words listed: {args.filepath}")

        # Check if the file exists before proceeding
        if not os.path.exists(args.filepath):
            print(f"Error: The file '{args.filepath}' does not exist.")
            return

        # Load the data from the specified file
        words = import_candidate_file(args.filepath)

        # Initialize variable to hold list of found word data
        word_data = []

        # Scrape data to populate word entries
        if not words.empty:
            print(f"Processing {len(words)} words...")
            for korean_word in words:
                word_data.append(scrape_naver_dict(korean_word))
        else:
            print("No words in list to process. Exiting.")

        # Setup MongoDB database and start connection
        collection = setup_database()
        # <--- we're here trying to pass data on to the database