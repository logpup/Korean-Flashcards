# Python standard library imports
import pprint
from typing import List, Dict, Any, Optional

# Third-part library imports
from pymongo.collection import Collection

# Internal library methods imports
from db.models import KoreanWord
from db.crud import get_value, set_value, append_value, create_document
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

def retrieve_en_definition(collection: Collection, korean_word: str):
    
    # Retrieve word data from the document for the specified word
    word_data = get_value(collection, korean_word, "word_data")

    # Isolate scraped data from Naver's Korean-English Dictionary "Word Idiom" page
    naver_en_word_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "word_idiom"
    ]
    # Target the most recent entry
    page_data = _most_recent_value(naver_en_word_data).get("page_data", [])

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

    # Isolate scraped data from Naver's Korean-English Dictionary "Example" page
    naver_en_example_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "example"
    ]
    # Target the most recent entry
    page_data = _most_recent_value(naver_en_example_data).get("page_data", [])
    
    # Initalize variable to store definitions
    examples = []

    # Take first two examples
    two_examples = page_data[:2]

    # Iterate through each to retrieve both native and translated senteces
    for example_data in two_examples:
        english_sentence = example_data.get("english_sentence")
        korean_sentence = example_data.get("korean_sentence")
        # Append each pair to list of examples
        example = {
            "english_sentence": english_sentence,
            "korean_sentence": korean_sentence            
        }
        examples.append(example)

    return examples

def retrieve_hanja(collection: Collection, korean_word: str):
    # Retrieve word data from the document for the specified word
    word_data = get_value(collection, korean_word, "word_data")

    # Isolate scraped data from Naver's Korean-English Dictionary "Word Idiom" page
    naver_en_word_data = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "word_idiom"
    ]
    # Target the most recent entry
    page_data = _most_recent_value(naver_en_word_data).get("page_data", [])

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
    hanja = retrieve_hanja(collection, korean_word)
    en_definition = retrieve_en_definition(collection, korean_word)
    en_example_sentence = retrieve_en_examples(collection, korean_word)

    set_value(collection, korean_word, "hanja", hanja)
    set_value(collection, korean_word, "en_definition", en_definition)
    set_value(collection, korean_word, "en_example_sentence", en_example_sentence)

def retrieve_krdict_hanja_idiom_pairs(word_data, korean_word: str):
    # Isolate data from Korean Basic Dictionary API calls
    krdict_word_data_list = [
        data for data in word_data
        if data.get("source_name") == "Korean Basic Dictionary"
        and data.get("source_url") == "https://krdict.korean.go.kr"
        and data.get("param_part") == "word"
    ]
    # Initialize list to hold hanja-idiom pairs
    krdict_hanja_idiom_pairs = []

    # Target the most recent entry
    if krdict_word_data_list is not None:
        # Retrieve the most recent Korean Basic Dictionary entry
        krdict_page_data = _most_recent_value(krdict_word_data_list).get("page_data", [])
        # Isolate word items that match the korean_word string
        krdict_word_items = [entry for entry in krdict_page_data if entry.get("word") == korean_word]

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
                pair = {
                    "hanja": origin,
                    "senses": senses
                }
                krdict_hanja_idiom_pairs.append(pair)
        return krdict_hanja_idiom_pairs
    else:
        krdict_hanja_idiom_pairs = None
    return krdict_hanja_idiom_pairs

def retrieve_naver_dict_hanja_idiom_pairs(word_data, korean_word: str):
    # Isolate scraped data from Naver's Korean-English Dictionary "Word Idiom" page
    naver_dict_en_word_data_list = [
        data for data in word_data
        if data.get("source_name") == "Naver Dictionary"
        and data.get("source_url") == "naver.dict.com"
        and data.get("source_region") == "en"
        and data.get("source_page") == "word_idiom"
    ]

    # Initalize variable to store pairs
    naver_dict_hanja_idiom_pairs = []
    
    if naver_dict_en_word_data_list is not None:
        # Target the most recent Naver Dictionary entry
        naver_dict_page_data = _most_recent_value(naver_dict_en_word_data_list).get("page_data", [])
        # Take entries where only the korean_word key matches the passed korean_word value
        naver_dict_word_items = [entry for entry in naver_dict_page_data if entry.get("korean_word") == korean_word]

        # Append each hanja-idioms pair to the list of pairs
        for word_item in naver_dict_word_items:
            # Retrieve hanja value
            hanja = word_item.get("hanja")
            # Initialize variable to store each sense
            senses = []
            senses = word_item.get("senses")
            # Initalize dictionary data to store hanja and its senses
            pair = {
                "hanja": hanja,
                "senses": senses
            }
            naver_dict_hanja_idiom_pairs.append(pair)

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
            pairs = None
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
    word_data = await lookup_entry(korean_word, language)
    for data in word_data:
        if data:
            append_value(collection, korean_word, "word_data", word_data)
    set_word_attributes(collection, korean_word)

def stage_flashcard(collection: Collection, korean_word: str, card_type: Optional[str]=None):
    if card_type is None:
        flashcard_type = "anki"

    if flashcard_type == "anki":
        flashcard_data = query_anki_flashcard_data(collection, korean_word)
        flashcard_note = create_anki_card(flashcard_data)
        return flashcard_note