# Standard Python library imports
from pathlib import Path
import datetime
import asyncio

# Third-party external library imports
import typer
from typing import Optional
from rich.console import Console
from InquirerPy import inquirer
from InquirerPy.exceptions import InvalidArgument
from pymongo.errors import OperationFailure

# Internal library methods imports
from data_utils.data_loader import import_candidate_file
from db.connection import connect_server, retrieve_collection
from db.crud import document_exists, create_document, append_value
from logic.logic_lookup import lookup_entry
from logic.logic_processor import set_word_attributes, query_anki_flashcard_data
from db.models import KoreanWord
from anki.card_generator import create_anki_card


# Create a Typer app instance
app = typer.Typer(
    name="dolphin",
    help="A Korean flashcard generation CLI app."
)

# Use a Rich console for pretty printing
console = Console()

@app.command(
    name="generate",
    help="Generates a flashcard file from an input file." 
)
def generate_flashcards(
    input_file: Path = typer.Argument(
        ..., help="Name of file with list of Korean words."
    ),
    directory: Optional[Path] = typer.Option(
        None, "--directory", "-d", help="The directory to save the output file."
    ),
    filename: Optional[str] = typer.Option(
        None, "--filename", "-f", help="The name of the output flashcard file."
    ),
    type: Optional[str] = typer.Option(
        None, "--type", "-t", help="The type of flashcard file to generate (e.g. Anki, Quizlet)"
    ),
):
    """
    Process an input file to generate a flashcard file
    """
    console.print(f"\n[bold green]Processing input file:[/] {input_file}")
    
    # Save Korean words from an input file to a list
    word_list = import_candidate_file(input_file)

    # Connect to the MongoDB server and retrieve specified collection
    client = connect_server()
    collection = retrieve_collection(client)

    # Seperate words already in the server from new words to scrape
    console.print("[bold blue]Checking to see which words are already in stored in the database...[/]")
    
    if collection is not None:
        try:
            # Initialize variables to hold seperate list of words
            existing_words = []
            new_words_list = []

            for word in word_list:
                if document_exists(collection, word):
                    existing_words.append(word)
                else:
                    new_words_list.append(word)

            # Iterate through list of words and source data entries
            console.print("[bold blue]Scraping various sources for data on Korean words and phrases...[/]")
            
            # Initalize list to hold deck of flashcards
            deck_data = []
            
            for new_word in new_words_list:

                # Create entry in database if word document does not exist
                if not document_exists(collection, new_word):
                    word_obj = KoreanWord(
                        word=new_word,
                    )
                    create_document(collection, word_obj)
                    
                    word_data = lookup_entry(new_word) # Search through sources
                    for data in word_data:
                        append_value(collection, new_word, "word_data, data")
                    set_word_attributes(collection, new_word) # Set word attributes in database

                # Append data to the database if entry already exists     
                else:
                    word_data = lookup_entry(new_word) # Search through sources
                    for data in word_data:
                        append_value(collection, new_word, "word_data", data)
                    set_word_attributes(collection, new_word) # Set word attributes in database
                
                flashcard_data = query_anki_flashcard_data(collection, new_word)
                note = create_anki_card(flashcard_data)
                deck_data.append(note)

            # ----
            try:
                selected_words = inquirer.checkbox(
                    message="Select the word to include in the "
                )
            

        except OperationFailure as e:
            print(f"ERROR: Operation failed. {e}")
        
        finally:
            # Close the connection cleanly
            if collection is not None:
                collection.database.client.close()
                print("\nDatabase connection closed.")
    else:
        print("Could not proceed with database operations due to a connection error.")

    

    if directory and filename:
        output_file_path = directory / filename
        console.print(f"[bold blue]Exporting flashcard file to:[/] {output_file_path}")
        console.print(f"[bold blue]Flashcard type selected:[/] {type}")
        # Here you would add the logic to export the file to the specified path
    else:
        console.print("[bold yellow]Note:[/] Output directory and filename not specified. No file will be saved.")

app()