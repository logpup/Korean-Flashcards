# Python standard library imports
import datetime
import sys
import os

# Third-part library imports
from pymongo.collection import Collection
from pymongo.errors import OperationFailure


#Imported modules from other files
from config.env_loader import load_environment_variables
from db.connection import connect_server, retrieve_collection

# --- Import from sibling modules for testing ---
# NOTE: If you run this file directly, you may need to adjust the path 
# based on your project's root directory structure to correctly import 
# 'connect_server' and 'retrieve_collection'.
load_environment_variables()
try:
    # Attempt relative import assuming this is run as part of a package
    from .connection import connect_server, retrieve_collection 
except ImportError:
    # Fallback/standalone execution guide
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    try:
        from db.connection import connect_server, retrieve_collection
    except ImportError:
        print("WARNING: Could not import connection functions. Test will not run.")
        connect_server = None
        retrieve_collection = None


def delete_all_documents(db_collection: Collection) -> int:
    """
    Deletes all entries from the specified MongoDB collection using delete_many({}).

    This operation is fast but irreversible. It is equivalent to truncating the table.

    Args:
        db_collection: The MongoDB Collection object (e.g., the 'korean_words' collection).

    Returns:
        The count of documents deleted (int), or -1 if an error occurred.
    """
    if db_collection is None:
        print("ERROR: Collection object is None. Cannot perform deletion.")
        return -1
        
    print(f"\n--- Attempting to clear collection: '{db_collection.name}' ---")
    
    try:
        # The query {} matches ALL documents in the collection
        result = db_collection.delete_many({})
        deleted_count = result.deleted_count
        print(f"✅ Success! Deleted {deleted_count} documents from '{db_collection.name}'.")
        return deleted_count
    except OperationFailure as e:
        print(f"❌ Error during mass deletion operation: {e}")
        return -1
    except Exception as e:
        print(f"❌ An unexpected error occurred during mass deletion: {e}")
        return -1

# --- Test Demonstration Function ---

def test_delete_all():
    """
    Demonstrates the use of delete_all_documents by inserting sample data
    and then clearing the collection using the connection module helpers.
    """
    if connect_server is None or retrieve_collection is None:
        print("Test aborted: Required connection functions are not available.")
        return
        
    print("\n" + "="*50)
    print("BEGINNING DELETE ALL DEMONSTRATION")
    print("="*50)

    # 1. Connect to the server
    client = connect_server()
    if client is None:
        print("Test failed: Could not connect to MongoDB.")
        return
    
    # 2. Retrieve the collection (defaults to 'korean_words')
    collection = retrieve_collection(client)
    if collection is None:
        print("Test failed: Could not retrieve collection.")
        client.close()
        return

    # --- SETUP: Insert sample data ---
    print("\n[SETUP] Inserting 3 sample documents...")
    sample_data = [
        {"word": "안녕하세요", "meaning": "hello", "created_at": datetime.datetime.now()},
        {"word": "감사합니다", "meaning": "thank you", "created_at": datetime.datetime.now()},
        {"word": "사랑", "meaning": "love", "created_at": datetime.datetime.now()}
    ]
    
    # Ensure collection is empty before setup to avoid double-counting
    collection.delete_many({}) 
    
    collection.insert_many(sample_data)
    initial_count = collection.count_documents({})
    print(f"       Initial document count: {initial_count}")
    
    # 3. Perform the mass deletion
    deleted_count = delete_all_documents(collection)

    # 4. Verification
    print("\n[VERIFICATION]")
    final_count = collection.count_documents({})
    
    if deleted_count == initial_count and final_count == 0:
        print(f"       Verification successful: {deleted_count} documents deleted. Final count is {final_count}.")
    else:
        print(f"       Verification failed. Expected {initial_count} deleted, got {deleted_count}. Final count: {final_count}.")

    client.close()
    print("Test client connection closed.")
    print("="*50)


if __name__ == "__main__":
    # This block allows you to run this file directly to test the functionality.
    test_delete_all()
