# Standard Library Imports
import time
import os
import datetime
from typing import Dict, List, Optional
import unicodedata
from pathlib import Path

# Third Party Library Imports
import genanki

def _to_superscript_digit(n):
    """Converts a number to its superscript string representation."""
    superscript_str = ''
    for char in str(n):
        try:
            # Find the full name of the character (e.g., 'DIGIT ONE')
            char_name = unicodedata.name(char)
            # Replace 'DIGIT' with 'SUPERSCRIPT' and get the new character
            superscript_name = char_name.replace('DIGIT', 'SUPERSCRIPT')
            superscript_char = unicodedata.lookup(superscript_name)
            superscript_str += superscript_char
        except (KeyError, ValueError):
            # Fallback for non-digit characters or those without a superscript form
            superscript_str += char
    return superscript_str

def create_anki_card(word_data: Dict) -> genanki.Note:
    """
    Creates a single Genanki Note (Anki card).

    This function defines a simple Anki model with two fields: 'Question' and 'Answer'.
    A Note is an instance of this model, containing the actual text for the card.

    Args:
        front_text: The text for the front of the card (the question).
        back_text: The text for the back of the card (the answer).

    Returns:
        A genanki.Note object representing a single Anki card.
    """
    # Extract and initialize variables to hold data
    korean_word = word_data.get("korean_word")
    entries = word_data.get("entries") # These are the hanja and idiom pairs
    example_sentences = word_data.get("examples")

    # First, create the string literal for the hanja and idiom pairs
    entries_string = ""
    if entries is not None:
        for entry in entries.values():
            # Print out hanja to entries_string
            hanja = entry.get("hanja")
            if hanja:
                entries_string += f"<span class='hanja'> {hanja} </span> "
            # Print out each sense with an index number if more than one
            senses = entry.get("senses")
            if senses:
                senses_list = []
                if len(senses) > 1:
                    for idx, sense in enumerate(senses, start=1):
                        idx_sup = _to_superscript_digit(idx)
                        senses_list.append(f"<span class='senses'>{idx_sup} {sense}</span>")
                else:
                    senses_list.append(f"<span class='senses'>{senses[0]}</span>")
                # Join together entries with line breaks
                entries_string += "<br>".join(senses_list)

    # Second, create the string literal for the example sentences
    example_sentences_string = ""
    if example_sentences:
        examples_list = []
        for idx, example in enumerate(example_sentences.values(), start=1):
            english_sentence = example.get('english_sentence')
            korean_sentence = example.get('korean_sentence')
            idx_sup = _to_superscript_digit(idx)
            examples_list.append(f"<span class='english_sentence'>{idx_sup} {english_sentence}</span><br><span class='korean_sentence'>{korean_sentence}</span><br><br>")
        example_sentences_string = "<br>".join(examples_list)

    # Genanki requires a unique ID for the model. Using a timestamp is a reliable
    # way to ensure uniqueness, especially if you plan to create multiple decks.
    # The ID must be a large positive integer.
    model_id = int(time.time() * 1000)

    # Define the structure of the Anki card (the 'model').
    # This includes the fields and how the card will look.
    my_model = genanki.Model(
        model_id,
        'Korean-English (w. Hanja) Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Definitions'},
            {'name': 'Examples'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': "<span class='word'>{{Word}}</span>",
                'afmt': "{{FrontSide}}<hr id='answer'>{{Definitions}}<br><br><br>{{Examples}}",
            },
        ],
        css='''
            .card {
                font-family: NanumGothic;
                font-size: 18pt;
                text-align: left;
	            color: black;
	            background-color: white;
            }

            .word {
            	font-size: 18pt;
            	color: #1B4789;
            	background: #E3F4FF
            }

            .hanja {
            	font-family: 'Microsoft YaHei';
            	font-size: 16pt;
            	font-weight: bold;
            	color: #666;
            }

            .senses {
            	font-size: 14pt;
            	font-weight: bold;
            }

            .examples {
            	color: black;
            }

            .english_sentence {
                font-size: 12pt;

            }
            .korean_sentence {
                font-size: 10pt;
            }

        '''
    )

    # Create a new note (an instance of the model) with the provided text.
    my_note = genanki.Note(
        model=my_model,
        fields=[korean_word, entries_string, example_sentences_string]
    )

    return my_note

def create_anki_deck(deck_name: str, cards: List[genanki.Note], deck_path: Path):
    """
    Collates a list of Genanki Notes (cards) into a single Anki deck file (.apkg).

    Args:
        deck_name: The name of the Anki deck to be created.
        cards: A list of genanki.Note objects to include in the deck.
        output_filepath: The full path and filename for the output .apkg file.
                         Example: "my_anki_deck.apkg"
    """
    # Genanki requires a unique ID for the deck. A timestamp is a good choice.
    deck_id = int(time.time() * 1000) + 1 # Ensure this ID is different from model_id

    # Create the deck container.
    my_deck = genanki.Deck(deck_id, deck_name)
    # Add each card to the deck.
    for card in cards:
        my_deck.add_note(card)

    # Package the deck into an .apkg file.
    try:
        genanki.Package(my_deck).write_to_file(deck_path)
        print(f"Successfully created Anki deck: '{deck_path}'")
    except Exception as e:
        print(f"An error occurred while writing the deck: {e}")

def export_anki_file(deck_data: List, fn: Optional[str], dir: Optional[Path]):
    deck_name = ""
    filename = ""
    
    # Handle filename
    if fn:
        deck_name = fn
        filename = f"{deck_name}.apkg"
    else:
        # Format date output
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d-%H-%M-%S")
        # Set as deck and file names
        deck_name = f"flashcards-{formatted_date}"
        filename = f"{deck_name}.apkg"
    
    # Handle directory
    if dir and str(dir) != ".":  # Check if dir parameter was provided and not default
        directory_path = Path(dir)
    else:
        directory_path = Path(".")
    
    # Ensure directory exists
    directory_path.mkdir(parents=True, exist_ok=True)
    
    # Create full path
    deck_path = directory_path / filename
    
    create_anki_deck(deck_name, deck_data, deck_path)