import pymongo
from scraping.scraping_naver_dict import scrape_naver_dict

def add_naver_dict_entry(collection, entry):

    """
    Retrieves all flashcards from the collection and prints them.
    """
    if collection is None:
        print("Cannot retrieve flashcards. Database connection failed.")
        return

    print("\n--- All Flashcards ---")
    # The find() method returns a cursor, which can be iterated.
    for flashcard in collection.find():
        print(f"Question: {flashcard['question']}")
        print(f"Answer: {flashcard['answer']}\n")