# Python standard library imports
import pprint
from typing import List, Dict, Any, Optional

# Third-part library imports
from pymongo.collection import Collection

# Internal library methods imports
from db.connection import connect_server, retrieve_collection
from db.crud import get_value

def most_recent_value(word_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
    page_data = most_recent_value(naver_en_word_data).get("page_data", [])

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

def retrieve_en_example(collection: Collection, korean_word: str):
   
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
    page_data = most_recent_value(naver_en_example_data).get("page_data", [])
    
    # Initalize variable to store definitions
    examples = []

    # Take first two examples
    two_examples = page_data[:2]

    # Iterate through each to retrieve both native and translated senteces
    for example in two_examples:
        korean_sentence = example.get("korean_sentence")
        english_sentence = example.get("english_sentence")
        # Append each pair to list of examples
        examples.append([korean_sentence, english_sentence])

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
    page_data = most_recent_value(naver_en_word_data).get("page_data", [])

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

# Connect to server and initialize the korean_words collection
client = connect_server()
collection = retrieve_collection(client)
korean_word = "만족"

retrieve_hanja(collection, korean_word)


"""
1. look up the word
2. send data over to be stored in the database
3. query from results
4. populate word attributes
5. use word_attributes to make flashcards
6. send flaschards made this sessions to database
7. export flashcard file
"""
"""
korean_word

hanja_1
english_idioms_1

hanja_2
english_idioms_2

example_sentence_1
example_translation_1

example_sentence_2
example_translation_2
"""