import asyncio

from pymongo.errors import OperationFailure

from db.connection import connect_server, initialize_collection, retrieve_collection
from db.crud import create_document, delete_document, document_exists, update_value, append_value, print_all_documents
from db.models import ScrapedPage, KoreanWord
from scraping.scraping_naver_dict import scrape_naver_dict

# Connect to server and initialize the korean_words collection
client = connect_server()
collection = retrieve_collection(client)

if collection is not None:
    try:
        # Example data for this test
        korean_word = "만족"

        # Create entry if word does not exist
        if not document_exists(collection, korean_word):
            word_obj = KoreanWord(
                 word=korean_word,
            )
            create_document(collection, word_obj)

        # Append data if entry exists     
        word_data = asyncio.run(scrape_naver_dict(korean_word))
        for data in word_data:
            append_value(collection, korean_word, "word_data", data)
            
    except OperationFailure as e:
        print(f"ERROR: Operation failed. {e}")
        
    finally:
        # Close the connection cleanly
        if collection is not None:
            collection.database.client.close()
            print("\nDatabase connection closed.")
else:
    print("Could not proceed with database operations due to a connection error.")
