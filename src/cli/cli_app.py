# Standard Python library imports
from pathlib import Path
import asyncio
import concurrent.futures
from typing_extensions import Annotated

# Third-party external library imports
import typer
from rich.console import Console
from InquirerPy import inquirer
from pymongo.errors import OperationFailure

# Internal library methods imports
from data_utils.data_loader import import_candidate_file
from db.connection import connect_server, retrieve_collection
from db.crud import document_exists, create_document, append_value
from logic.logic_lookup import lookup_entry
from logic.logic_processor import set_word_attributes, query_anki_flashcard_data
from db.models import KoreanWord
from anki.card_generator import create_anki_card, export_anki_file
from cli.cli_inquirer import ask_to_aggregate_data

# Create a Typer app instance
app = typer.Typer(
    name="dolphin",
    help="A Korean flashcard generation CLI app."
)

# Use a Rich console for pretty printing
console = Console()

async def _generate_flashcards_async(
    input_file: Path,
    directory: Path,
    filename: str,
    card_type: str,
):
    """
    Async implementation of flashcard generation
    """
    console.print(f"\n[bold green]Processing input file:[/] {input_file}")
    console.print(f"[bold cyan]Output directory:[/] {directory}")
    console.print(f"[bold cyan]Filename:[/] {filename}")
    
    # Save Korean words from an input file to a list
    word_list = import_candidate_file(input_file)
    # Connect to the MongoDB server and retrieve specified collection
    client = connect_server()
    collection = retrieve_collection(client)
    # Seperate words already in the server from new words to scrape
    console.print("[bold blue]Checking to see which words are already in stored in the database...[/]")
    
    if collection is not None:
        try:
            # Seperate from new words, words that are already in the database
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
                # Create a new MongoDB document for each new word
                word_obj = KoreanWord(
                    word=new_word,
                )
                create_document(collection, word_obj)
                
                # Process each new word (source references, append values, set attributes)
                word_data = await lookup_entry(new_word) # Search through sources
                for data in word_data:
                    append_value(collection, new_word, "word_data", data)
                set_word_attributes(collection, new_word)
                
                # Create flashcard and append to deck
                flashcard_data = query_anki_flashcard_data(collection, new_word)
                note = create_anki_card(flashcard_data)
                deck_data.append(note)

            try:
                selected_words_list = await inquirer.checkbox(
                    message="These words are already in the database. Select which entries you would still want to include for this deck.\n[Space] to Select\n[Enter] to Confirm Entry",
                    choices=existing_words,
                ).execute_async()

                should_aggregate_data = await ask_to_aggregate_data()

                if selected_words_list:
                    for selected_word in selected_words_list:
                        if should_aggregate_data:
                        # Process each selected word (source references, append values, set attributes)
                            word_data = await lookup_entry(selected_word) # Search through sources
                            for data in word_data:
                                append_value(collection, selected_word, "word_data", data)
                            set_word_attributes(collection, selected_word) # Set word attributes in database
                        # Create flashcard and append to deck
                        flashcard_data = query_anki_flashcard_data(collection, selected_word)
                        note = create_anki_card(flashcard_data)
                        deck_data.append(note)

            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user. Exiting...")
            except EOFError:
                print("\n\nEnd of input received. Exiting...")

            # Finally, export the file
            console.print(f"[bold magenta]Exporting to directory:[/] {directory}")
            console.print(f"[bold magenta]Directory type:[/] {type(directory)}")
            console.print(f"[bold magenta]Directory exists:[/] {directory.exists()}")
            
            # Create directory if it doesn't exist
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                console.print(f"[bold green]Created directory:[/] {directory}")
            
            export_anki_file(deck_data, filename, directory)

        except OperationFailure as e:
            print(f"ERROR: Operation failed. {e}")
        
        finally:
            # Close the connection cleanly
            if collection is not None:
                collection.database.client.close()
                print("\nDatabase connection closed.")
    else:
        print("Could not proceed with database operations due to a connection error.")

@app.command(
    name="generate",
    help="Generates a flashcard file from an input file." 
)
def generate_flashcards(
    input_file: Annotated[Path, typer.Argument(
        ..., help="Name of file with list of Korean words."
    )],
    directory: Annotated[Path, typer.Option(
        "--directory", "-d", help="The directory to save the output file."
    )] = Path("."),
    filename: Annotated[str, typer.Option(
        "--filename", "-f", help="The name of the output flashcard file."
    )] = "",
    type: Annotated[str, typer.Option(
        "--type", "-t", help="The type of flashcard file to generate (e.g. Anki, Quizlet)"
    )] = "",
):
    """
    Process an input file to generate a flashcard file
    """
    # Handle both cases: running in an existing event loop or not
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        # If we reach this line, there's already a running loop
        # We need to run the coroutine in a separate thread
        
        def run_in_thread():
            # Create a new event loop in this thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_generate_flashcards_async(input_file, directory, filename, type))
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            future.result()  # Wait for completion
            
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        asyncio.run(_generate_flashcards_async(input_file, directory, filename, type))

@app.command(
    name="test",
    help="Hello World"
)
def test(
    name: Annotated[str, typer.Argument(help="The name to greet.")] = "World"
):
    """
    A simple command that greets the user
    """
    typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()