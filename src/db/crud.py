# Python standard library imports
import datetime

# Third-part library imports
from pymongo.collection import Collection

from db.models import ScrapeData, KoreanWord

def entry_exists(db_collection: Collection, word: str) -> bool:
    """
    Returns True if an entry for the given word exists in the collection.
    """
    return db_collection.find_one({"word": word}) is not None

def create_entry(db_collection: Collection, korean_word: KoreanWord):
    """
    Inserts a KoreanWord instance into the MongoDB collection.
    """
    # Convert dataclass to dictionary for MongoDB
    word_dict = korean_word.__dict__.copy()
    # Inserts KoreanWord data type into collection
    db_collection.insert_one(word_dict)

def delete_entry(db_collection: Collection, word: str):
    """
    Delete a KoreanWord entry from the MongoDB collection by word.
    """
    db_collection.delete_one({"word": word})
    
def update_entry(db_collection: Collection, word: str, key: str, value):
    """
    Update a KoreanWord entry in the collection by word and attribute name.
    """
    db_collection.update_one(
        {"word": word},           # Find the document by the 'word' field
        {"$set": {key: value}}    # Set the specified attribute to the new value
    )

def append_entry(db_collection: Collection, word: str, key: str, value):
    """
    Append an entry for a KoreanWord instance in the MongoDB collection.
    """
    db_collection.update_one(
        {"word": word},         # Find the document by the 'word' field
        {"$push": {key: value}} # Append the speciied attribute with new entry
    )

def set_entry(db_collection: Collection, word: str, key: str, value):
    """
    Set the entry for a KoreanWord instance in the MongoDB collection.
    """
    db_collection.update_one(
        {"word": word},         # Find the document by the 'word' field
        {"$set": {key, value}}, # Set the specified attribute with the value
        {"last_update": datetime.datetime.now()}
    )

    # If first instance, also set created_at value
    created = db_collection.find_one(
        {"word": word},
        {"created_at": { "exists": True }}
    )
    
    if not created:
        db_collection.update_one(
            {"word": word},
            {"$set": {"created_at", datetime.datetime.now()}}
        )

def query_entry(db_collection: Collection, word: str, key: str):
    """
    Retrieve value for the specified attribute for a KoreanWord instance in the MongoDB collection
    """
    db_collection.find_one(
        {"word": word},
        {key: 1, "id_": 0}
    )

def print_all_documents(collection):
    """
    Prints all documents in the specified MongoDB collection.
    """
    if collection is None:
        print("Cannot print documents: MongoDB collection is not available.")
        return

    print("\n--- All Documents in the Collection ---")
    try:
        # The find() method returns a cursor, which is an iterable
        # that allows you to loop through all documents.
        documents = collection.find({})
        
        # Check if the collection is empty
        if collection.count_documents({}) == 0:
            print("The collection is empty.")
            return

        for doc in documents:
            # Print each document
            print(doc)
            
    except Exception as e:
        print(f"An error occurred while fetching documents: {e}")
    finally:
        # A good practice is to close the client connection after you're done.
        # However, in this simple script, the client goes out of scope anyway.
        # For a more complex application, client.close() is recommended.
        pass