# Standard Python Library Imports
import os
from pathlib import Path
from typing import List, Optional

# External third-party Imports
from bs4 import BeautifulSoup
from rich.console import Console
from integration.anki.card_generator import export_anki_file

def _import_txt(filepath):
    """
    Internal function to import a simple text file.

    The moethod performs the following steps;
    1. Opens and reads the specified text file.
    2. Strips leading/trailing whitespaces and removes linebreak from each line.
    3. Filters out any empty lines.
    4. Create a pandas DataFrame where the cleaned lines are stored in the first column.
    """
    word_list = []  # Initalize empty list to send back if there is an error
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip().split(',', 1) for line in f if line.strip()]
            word_list = lines
            return word_list
    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
        return word_list
    except Exception as e:
        print(f"❌ Error importing TXT: {e}")
        return word_list

def _import_html(filepath):
    """
    Reads a local HTML file, removes linebreaks, and stores the contents of
    each line in a pandas DataFrame.

    The method performs the following steps:
    1. Opens and reads the specified HTML file.
    2. Strips leading/trailing whitespace and removes linebreaks from each line.
    3. Filters out any empty lines.
    4. Creates a pandas DataFrame where the cleaned lines are stored in the
       first column.
    """
    try:
        # Use a 'with' statement to open and read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Create the Beautiful Soup object for parsing
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the <body> tag
        body_tag = soup.body

        word_list = []  # Initialize empty list to send back if there is an error

        if body_tag:
            # Convert the body_tag object to a string before using replace()
            body_tag_string = body_tag.prettify()

            # Delete <body tags and replace them with an empty string
            body_tag_string = body_tag_string.replace('<body>', '').replace('</body>', '')
            # Replace <br> tags with a newline character for easy splitting
            clean_content = body_tag_string.replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '\n')
           
            # Split the string by the newline characters
            word_list = [word.strip() for word in clean_content.splitlines() if word.strip()]

            return word_list
    
    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
        return word_list
    except Exception as e:
        print(f"❌ Error importing HTML: {e}")
        return word_list

def import_candidate_file(filepath):
    """
    Imports Korean words from a variety of file types.
    
    Args:
        filepath (str): The path to the file containing the word list.
        
    Returns:
        word_list: A list of Korean words for futher processing
    """
    file_extension = os.path.splitext(filepath)[1].lower()

    if file_extension == '.txt':
        return _import_txt(filepath)
    elif file_extension == '.html':
        return _import_html(filepath)
    else:
        print(f"❌ Error: Unsupported file type: {file_extension}")
        word_list = []  # Initialize empty list to send back if there is an error
        return word_list
    
def export_flashcard_deck(deck_data: List, console: Console, filename: Optional[str] = None, directory: Optional[Path] = None, card_type: Optional[str] = None):

    # Set default filename if not provided
    if filename is None:
        filename = "flashcards.apkg"
    # Set default directory if not provided
    if directory is None:
        directory = Path(".")
    # Set default card type if not provided
    if card_type is None:
        card_type = "anki"
 
    # Create directory if it doesn't exist
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"[bold green]Created directory:[/] {directory}")
    
    if card_type == "anki":
        print(f"[bold magenta]Exporting Anki deck to:[/] {directory / filename}")
        export_anki_file(deck_data, filename, directory)