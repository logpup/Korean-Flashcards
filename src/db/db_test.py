from pymongo.errors import OperationFailure

from db.connection import connect_to_server, initialize_collection
from db.crud import create_entry, delete_entry, entry_exists, update_entry, append_entry, print_all_documents
from db.models import ScrapeData, KoreanWord
from scraping.scraping_naver_dict import scrape_naver_dict

# Connect to server and initialize the korean_words collection
client = connect_to_server()
collection = initialize_collection(client)

if collection is not None:
    try:
        # Example data for this test
        korean_word = "완공"
        
        word_data = scrape_naver_dict(korean_word)

        # Append data if entry exists, if not 
        if not entry_exists(collection, korean_word):
            word_obj = KoreanWord(
                 word=korean_word,
            )
            create_entry(collection, word_obj)

        append_entry(collection, korean_word, "word_data", word_data)

        print_all_documents(collection)
    except OperationFailure as e:
        print(f"ERROR: Operation failed. {e}")
        
    finally:
        # Close the connection cleanly
        if collection:
            collection.database.client.close()
            print("\nDatabase connection closed.")
else:
    print("Could not proceed with database operations due to a connection error.")
