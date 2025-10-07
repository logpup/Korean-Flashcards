# Standard Python library imports
from pathlib import Path
import asyncio
import concurrent.futures
from typing import Optional
from typing_extensions import Annotated

# Third-party external library imports
import typer
from rich.console import Console
from pymongo.errors import OperationFailure

# Internal library methods imports
from db.connection import connect_server, retrieve_collection
from db.crud import document_exists
from cli.cli_inquirer import ask_to_aggregate_data, select_words, input_user_word_data
from logic.logic_processor import process_word, query_anki_flashcard_data, stage_flashcard, check_missing_values
from logic.logic_file_io import import_candidate_file, export_flashcard_deck

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
    language: Optional[str] = None,
    card_type: Optional[str] = None,
):
    """
    Async implementation of flashcard generation
    """
    console.print(f"\n[bold green]Processing input file:[/] {input_file}")
    console.print(f"[bold cyan]Output directory:[/] {directory}")
    console.print(f"[bold cyan]Filename:[/] {filename}")

    # Connect to the MongoDB server and retrieve specified collection
    client = connect_server()
    collection = retrieve_collection(client)

    # Save Korean words from an input file to a list
    word_list = import_candidate_file(input_file)

    # Seperate words that already in the server from entirely new words
    console.print("[bold blue]Checking to see which words are already in stored in the database...[/]")
    if collection is not None:
        try:
            existing_words_list = []
            new_words_list = []
            for word in word_list:
                if document_exists(collection, word):
                    existing_words_list.append(word)
                else:
                    new_words_list.append(word)

            # Iterate through list of words and source data entries
            console.print("[bold blue]Scraping various sources for data on Korean words and phrases...[/]")
            # Initalize list to hold deck of flashcards
            deck_data = []
            
            # Initialize list to hold words where entries missing
            empty_values_word_info_list = []

            # Iterate through new words
            for new_word in new_words_list:
                # Process each new word (source references, append values, set attributes)
                data_found = await process_word(collection, new_word, language)
                # Check if any data was found
                empty_values_word_info = check_missing_values(collection, new_word, data_found)
                if empty_values_word_info:
                    empty_values_word_info_list.append(empty_values_word_info)
                else:
                    # If all values entered, append to deck_data
                    flashcard_note = stage_flashcard(collection, new_word, card_type)
                    if flashcard_note:
                        deck_data.append(flashcard_note)

            # Process words that are already in the database
            if existing_words_list:
                try:
                    prompt_message = "These words are already in the database. Select which entries you would still want to include for this deck.\n[Space] to Select\n[Enter] to Confirm Entry"
                    response = await select_words(existing_words_list, prompt_message)
                    selected_words_list = response[0]
                    should_aggregate_data = await ask_to_aggregate_data()

                    if selected_words_list: 
                        for selected_word in selected_words_list:
                            if should_aggregate_data:
                                # Process each selected word (source references, append values, set attributes)
                                data_found = await process_word(collection, selected_word, language)
                                empty_values_word_info = check_missing_values(collection, selected_word, data_found)
                                if empty_values_word_info:
                                    empty_values_word_info_list.append(empty_values_word_info)
                                else:
                                    # If all values entered, append to deck_data
                                    flashcard_note = stage_flashcard(collection, selected_word, card_type)
                                    if flashcard_note:
                                        deck_data.append(flashcard_note)
                            else:
                                empty_values_word_info = check_missing_values(collection, selected_word, data_found=True)
                                if empty_values_word_info:
                                    empty_values_word_info_list.append(empty_values_word_info)
                                else:
                                    # Just stage the flashcard without processing
                                    flashcard_note = stage_flashcard(collection, selected_word, card_type)
                                    if flashcard_note:
                                        deck_data.append(flashcard_note)
                except KeyboardInterrupt:
                    print("\n\nOperation cancelled by user. Exiting...")
                except EOFError:
                    print("\n\nEnd of input received. Exiting...")
                except Exception as e:
                    print(f"\n\nAn error occurred: {e}. Exiting...")

            # Process words that are missing values
            if empty_values_word_info_list:  # Only process if there are words with missing values
                try:
                    # Have user select which words to write entries for
                    empty_value_word_list = [value["korean_word"] for value in empty_values_word_info_list]
                    prompt_message = "These words are missing entries. Select which entries you would want to input data for."
                    response = await select_words(empty_value_word_list, prompt_message)
                    selected_words_list = response[0]
                    # Narrow empty_word_info_list to just the words selected
                    selected_words_set = set(selected_words_list)
                    selected_word_info_list = [
                        value for value in empty_values_word_info_list
                        if value.get("korean_word") in selected_words_set
                    ]
                    # Prompt user to enter data for words selected
                    if selected_words_list:
                        for selected_word_info in selected_word_info_list:
                            # Process each selected word
                            await input_user_word_data(collection, selected_word_info)
                            # Append to deck_data
                            selected_word = selected_word_info["korean_word"]
                            flashcard_note = stage_flashcard(collection, selected_word, card_type)
                            if flashcard_note:
                                deck_data.append(flashcard_note)
                    # Append unselected word flashcard to the deck
                    unselected_words_list = response[1]
                    if unselected_words_list:
                        for unselected_word in unselected_words_list:
                            flashcard_note = stage_flashcard(collection, unselected_word, card_type)
                            if flashcard_note:
                                deck_data.append(flashcard_note)

                except KeyboardInterrupt:
                    print("\n\nOperation cancelled by user. Exiting...")
                except EOFError:
                    print("\n\nEnd of input received. Exiting...")
                except Exception as e:
                    print(f"\n\nAn error occurred: {e}. Exiting...")

            # Finally, export the file
            console.print(f"[bold magenta]Exporting to directory:[/] {directory}")
            console.print(f"[bold magenta]Directory type:[/] {type(directory)}")
            console.print(f"[bold magenta]Directory exists:[/] {directory.exists()}")
            
            export_flashcard_deck(deck_data, console, filename, directory, card_type)

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