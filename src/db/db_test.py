from pymongo.errors import OperationFailure

from db.connection import setup_database
from db.crud import create_entry, delete_entry, entry_exists, update_entry, append_entry, print_all_documents
from db.models import ScrapeData, KoreanWord


collection = setup_database()

if collection:
    try:
        # Example usage in your CLI logic
        '''
        korean_word = "완공"
        entry_data = [{"korean_word": "완공", "hanja": "完工"},
           {"korean_word": "완공하다", "hanja": "完工하다"}]
        if entry_exists():
            append_entry(collection, korean_word, "word_data", entry_data)
        else:
            word_obj = KoreanWord(
                 word=korean_word,
            )
            create_entry(collection, word_obj)
        '''
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
