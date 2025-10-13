# Python standard library imports
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# Third-part library imports
from pymongo.collection import Collection

# Internal library methods imports
from db.models import KoreanWord
from db.crud import get_value, set_value, append_value, create_document, document_exists
from logic.logic_lookup import lookup_entry
from integration.anki.card_generator import create_anki_card

def _most_recent_value(word_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Finds the dictionary entry with the most recent 'updated_at' timestamp.

    Args:
        word_data: A list of dictionaries, where each dictionary is expected to have
              an 'updated_at' key with a datetime object value.

    Returns:
        page_data: The dictionary with the latest timestamp, or None if the list is empty.
    """
    if not word_data:
        print("The list is empty. No entry to return.")
        return None

    try:
        # Use the max() function with a lambda key.
        # The lambda function `lambda x: x['updated_at']` tells max() to compare
        # each dictionary `x` based on the value of its 'updated_at' key.
        page_data = max(word_data, key=lambda x: x['updated_at'])
        return page_data
    except KeyError:
        # Handle the case where an entry is missing the 'updated_at' key.
        print("Error: One or more entries are missing the 'updated_at' key.")
        return None


def retrieve_en_definitions(collection: Collection, korean_word: str):
    
    # Retrieve word data from the document for the specified word
    word_data = get_value(collection, korean_word, "word_data")

    # Check if word_data is None before attempting to iterate
    if word_data is None:
        return []

    # Isolate scraped data from Naver's Korean-English Dictionary "Word Idiom" page
    naver_en_word_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "word_idiom"
    ]
    # Target the most recent entry
    most_recent_entry = _most_recent_value(naver_en_word_data)
    if most_recent_entry is None:
        return []
    
    page_data = most_recent_entry.get("page_data", [])

    # Initalize variable to store definitions
    definitions = []

    # Take entries where only the korean_word key matches the passed korean_word value
    matched_words = [entry for entry in page_data if entry.get("korean_word") == korean_word]

    # Append each sense to the list of definitions
    for matched_word in matched_words:
        senses = matched_word.get("senses")
        for sense in senses:
            definitions.append(sense)

    return definitions

def retrieve_en_examples(collection: Collection, korean_word: str):
   
    # Retrieve word data from the document for the specified word
    word_data = get_value(collection, korean_word, "word_data")

    # Check if word_data is None before attempting to iterate
    if word_data is None:
        return []
    
    # Isolate scraped data from Naver's Korean-English Dictionary "Example" page
    naver_en_example_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "example"
    ]

    # Target the most recent entry
    most_recent_entry = _most_recent_value(naver_en_example_data)
    if most_recent_entry is None:
        return []
    page_data = most_recent_entry.get("page_data", [])
    
    # Initalize variable to store definitions
    examples = []

    # Take first two examples
    two_examples = page_data[:2]

    # Iterate through each to retrieve both native and translated sentences
    for example_data in two_examples:
        # Add type checking to handle strings vs dicts
        if isinstance(example_data, dict):
            english_sentence = example_data.get("english_sentence")
            korean_sentence = example_data.get("korean_sentence")
        else:
            # Handle case where example_data is a string (from manual entry error)
            print(f"Warning: Expected dict but got {type(example_data)}: {example_data}")
            continue
            
        # Append each pair to list of examples
        example = {
            "english_sentence": english_sentence,
            "korean_sentence": korean_sentence            
        }
        examples.append(example)

    return examples

def retrieve_hanjas(collection: Collection, korean_word: str):
    # Retrieve word data from the document for the specified word
    word_data = get_value(collection, korean_word, "word_data")

    # Check if word_data is None before attempting to iterate
    if word_data is None:
        print(f"No word_data found for '{korean_word}'. Cannot retrieve hanja.")
        return []

    # Isolate scraped data from Naver's Korean-English Dictionary "Word Idiom" page
    naver_en_word_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "word_idiom"
    ]

    # Target the most recent entry
    most_recent_entry = _most_recent_value(naver_en_word_data)
    if most_recent_entry is None:
        return []
    page_data = most_recent_entry.get("page_data", [])

    # Initalize variable to store definitions
    hanjas = []

    # Take entries where only the korean_word key matches the passed korean_word value
    matched_words = [entry for entry in page_data if entry.get("korean_word") == korean_word]

    # Append each hanja to the list of definitions
    for matched_word in matched_words:
        hanja = matched_word.get("hanja")
        if hanja:
            hanjas.append(hanja)

    print(f"{hanjas}")
    return hanjas


def set_word_attributes(collection: Collection, korean_word: str):
    hanja = retrieve_hanjas(collection, korean_word)
    en_definition = retrieve_en_definitions(collection, korean_word)
    en_example_sentence = retrieve_en_examples(collection, korean_word)

    if hanja is not None:
        set_value(collection, korean_word, "hanja", hanja)
    if en_definition is not None:
        set_value(collection, korean_word, "en_definition", en_definition)
    if en_example_sentence is not None:
        set_value(collection, korean_word, "en_example_sentence", en_example_sentence)


def retrieve_krdict_hanja_idiom_pairs(word_data, korean_word: str):
    # Isolate data from Korean Basic Dictionary API calls
    krdict_word_data = [
        data for data in word_data
        if data.get("source_name") == "Korean Basic Dictionary"
        and data.get("source_url") == "https://krdict.korean.go.kr"
        and data.get("param_part") == "word"
    ]
    
    # Target the most recent entry
    if krdict_word_data:
        # Retrieve the most recent Korean Basic Dictionary entry
        most_recent_entry = _most_recent_value(krdict_word_data)
        if most_recent_entry is None:
            return []
        krdict_page_data = most_recent_entry.get("page_data", [])

        # Isolate word items that match the korean_word string
        krdict_word_items = [entry for entry in krdict_page_data if entry.get("word") == korean_word]
        if krdict_word_items is None:
            return []
        
        # Initialize list to hold hanja-idiom pairs
        krdict_hanja_idiom_pairs = []
        # Append each hanja-idioms pair to the list of pairs
        for word_item in krdict_word_items:
            # Check if english idiom provided
            if "en_word" in word_item:
                # Retrieve origin value
                origin = word_item.get("origin")
                # Retrieve pos value
                pos = word_item.get("pos")
                # Retrieve en_word value
                en_word = word_item.get("en_word")
                # Add part of speech to idiom string
                idiom = f"[{pos}] {en_word}"
                # Initialize variable senses
                senses = []
                senses.append(idiom)
                # Initalize dictionary data to store hanja and its senses
                hanja_idiom_pair = {
                    "hanja": origin,
                    "senses": senses
                }
                krdict_hanja_idiom_pairs.append(hanja_idiom_pair)
            # If no english idiom provided, continue on
            else:
                continue
        if krdict_hanja_idiom_pairs:
            return krdict_hanja_idiom_pairs
        else:
            return []
    else:
        return []

def retrieve_naver_dict_hanja_idiom_pairs(word_data, korean_word: str):
    # Isolate scraped data from Naver's Korean-English Dictionary "Word Idiom" page
    naver_dict_en_word_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "word_idiom"
    ]

    if naver_dict_en_word_data:
        # Target the most recent Naver Dictionary entry
        most_recent_entry = _most_recent_value(naver_dict_en_word_data)
        if most_recent_entry is None:
            return []
        naver_dict_page_data = most_recent_entry.get("page_data", [])

        # Take entries where only the korean_word key matches the passed korean_word value
        naver_dict_word_items = [entry for entry in naver_dict_page_data if entry.get("korean_word") == korean_word]
        if naver_dict_word_items is None:
            return []
        
        # Initalize variable to store pairs
        naver_dict_hanja_idiom_pairs = []
        # Append each hanja-idioms pair to the list of pairs
        for word_item in naver_dict_word_items:
            # Initialize variable to store each sense
            senses = word_item.get("senses")
            if senses:
                # Retrieve hanja value
                hanja = word_item.get("hanja")
                # Initalize dictionary data to store hanja and its senses
                pair = {
                    "hanja": hanja,
                    "senses": senses
                }
                naver_dict_hanja_idiom_pairs.append(pair)
            # If senses list empty, continue through the for loop
            else:
                continue
        # Check if return list is empty
        if naver_dict_hanja_idiom_pairs:
            return naver_dict_hanja_idiom_pairs
        else:
            return []
    else:
        return []


def retrieve_hanja_idioms_pairs(collection: Collection, korean_word: str):
    """
    Retrieves hanja and the english definitions associated with that hanja context of
    a specified Korean word.

    Returns:
        pairs: a list of dictionary items containing the keys "hanja" and "senses" (a list of
        senses for the associated hanja context)
    """
    # Retrieve word data from the document for the specified word
    word_data = get_value(collection, korean_word, "word_data")
    if word_data is None:
        return[]

    # Initialize variable to store pairs
    pairs = []

    # Retrieve Korean Basic Dictionary data
    krdict_hanja_idiom_pairs = retrieve_krdict_hanja_idiom_pairs(word_data, korean_word)
    if krdict_hanja_idiom_pairs:
        pairs = krdict_hanja_idiom_pairs
    else:
        naver_dict_hanja_idiom_pairs = retrieve_naver_dict_hanja_idiom_pairs(word_data, korean_word)
        if naver_dict_hanja_idiom_pairs:
            pairs = naver_dict_hanja_idiom_pairs
        else:
            pairs = [{
                "hanja": "",
                "senses": [""]
            }]
    return pairs


def query_anki_flashcard_data(collection: Collection, korean_word: str) -> Dict:
    """
    Retrieves and formats flashcard data for a given Korean word.

    Args:
        collection: The database collection to query.
        korean_word: The Korean word to retrieve flashcard data for.

    Returns:
        flashcard_data: A dictionary containing three keys: "korean_word" for the
                   specified word, "entries" for the hanja-idiom pairs and "examples"
                   for English-Korean sentence examples.
    """

    # Retrieve values from the database
    hanja_idiom_pairs = retrieve_hanja_idioms_pairs(collection, korean_word)
    en_example_sentences = retrieve_en_examples(collection, korean_word)

    # Use a dicionary comprehension to index each entry
    entries = {
        f"entry_{idx}": {
            "hanja": pair.get("hanja"),
            "senses": pair.get("senses")
        }
        for idx, pair in enumerate(hanja_idiom_pairs, start=1)
    }

    # Use a dictionary comprehension to index each example
    examples = {
        f"example_{idx}": {
            "english_sentence": ex.get("english_sentence"),
            "korean_sentence": ex.get("korean_sentence"),
        }
        for idx, ex in enumerate(en_example_sentences, start=1)
    }

    # Initialize flashcard dictionary to hold the list of entries and examples
    flashcard_data = {"korean_word": korean_word, "entries": entries, "examples": examples}

    # print(f"Flashcard: {flashcard_data}")
    return flashcard_data


def initialize_word_document(collection: Collection, korean_word: str):
    # Create a new MongoDB document for each new word
    word_obj = KoreanWord(
        word=korean_word,
    )
    create_document(collection, word_obj)

async def process_word(collection: Collection, korean_word: str, language: Optional[str] = None):
    # Check if document for word exists
    exists = document_exists(collection, korean_word)

    # Create a document for the specified word if not
    if exists is False:
        initialize_word_document(collection, korean_word)

    # Aggregate data for specified word and save found entries as the list "word_data_objects"
    word_data_objects = await lookup_entry(korean_word, language)
    
    # Initialize a list to store dictionary representations
    word_data_list = []
    # Convert each dataclass object to a dictionary for MongoDB compatability
    for data_object in word_data_objects:
        if data_object:
            try:
                data_dict = asdict(data_object)
                word_data_list.append(data_dict)
            except TypeError:
                # Check if the object is already a dictionary
                if isinstance(data_object, Dict):
                    data_dict = data_object
                    word_data_list.append(data_dict)

    # Append each dictionary entry as a value for the key "word_data"
    if word_data_list:
        for word_data in word_data_list:
            append_value(collection, korean_word, "word_data", word_data)

    # Set values of note (e.g. hanja, definitions)
    set_word_attributes(collection, korean_word)

def process_user_entry(collection: Collection, korean_word: str, page_data: Dict):
    # Check if document for word exists
    exists = document_exists(collection, korean_word)

    # Create a document for the specified word if not
    if exists is False:
        initialize_word_document(collection, korean_word)
    
    if page_data:
        append_value(collection, korean_word, "word_data", page_data)
    
def check_missing_values(collection: Collection, korean_word: str, data_found: bool = False) -> Optional[Dict]:
    """
    Checks if a word document is missing critical values for flashcard creation.
    
    Args:
        collection: The MongoDB collection
        korean_word: The Korean word to check
        data_found: Whether data was found during processing (False means no data found)
        
    Returns:
        A dictionary with korean_word and missing_values if data is missing, None otherwise
    """
    # If data_found is False, we know data is missing
    if data_found is False:
        return {
            "korean_word": korean_word,
            "missing_values": ["entries", "examples"]
        }
    
    # Get the hanja-idiom pairs and examples
    hanja_idiom_pairs = retrieve_hanja_idioms_pairs(collection, korean_word)
    en_examples = retrieve_en_examples(collection, korean_word)
    
    missing_values = []
    
    # Check if entries are missing or empty
    if not hanja_idiom_pairs or hanja_idiom_pairs == [{"hanja": "", "senses": [""]}]:
        missing_values.append("entries")
    
    # Check if examples are missing or empty
    if not en_examples:
        missing_values.append("examples")
    
    # Return the info dict if there are missing values
    if missing_values:
        return {
            "korean_word": korean_word,
            "missing_values": missing_values
        }
    else:
        return None

def stage_flashcard(collection: Collection, korean_word: str, card_type: Optional[str]=None):
    if card_type is None:
        flashcard_type = "anki"
    else:
        flashcard_type = card_type

    if flashcard_type == "anki":
        flashcard_data = query_anki_flashcard_data(collection, korean_word)
        flashcard_note = create_anki_card(flashcard_data)
        return flashcard_note


# IMPORTANT: Test code should only run when this file is executed directly
# NOT when it's imported as a module
if __name__ == "__main__":
    # --- Test ---
    from db.connection import connect_server, retrieve_collection
    import asyncio
    import pprint

    client = connect_server()
    collection = retrieve_collection(client)

    korean_word = "월급 루펑"
    asyncio.run(process_word(collection, korean_word))
    flashcard_note = stage_flashcard(collection, korean_word)
    pprint.pprint(flashcard_note)