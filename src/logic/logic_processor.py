# Third-part library imports
from pymongo.collection import Collection

# Internal library methods imports
from db.crud import query_entry

def query_en_definition(collection: Collection, korean_word: str):
    # Retrieve value from word data
    collection.find().sort("update_at", -1).limit(1)
    query_entry(collection, korean_word, )
    korean_word
    """
    1. look up the word
    2. send data over to be stored in the database
    3. query from results
    4. populate word attributes
    5. use word_attributes to make flashcards
    6. send flaschards made this sessions to database
    7. export flashcard file
    """

def query_en_example(korean_word: str):
    korean_word

def query_hanja(korean_word: str):
    korean_word

korean_word = "라면"

query_en_definition

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