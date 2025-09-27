# Python standard library imports
import datetime
from dataclasses import asdict, is_dataclass
from typing import Dict, Any

# Third-part library imports
from pymongo.collection import Collection

# Internal library methods imports
from db.models import KoreanWord

def document_exists(db_collection: Collection, word: str) -> bool:
    """
    Returns True if an entry for the given word exists in the collection.
    """
    return db_collection.find_one({"word": word}) is not None

def create_document(db_collection: Collection, korean_word: KoreanWord):
    """
    Inserts a KoreanWord instance into the MongoDB collection.
    """
    # Convert dataclass to dictionary for MongoDB
    word_dict = korean_word.__dict__.copy()
    # Inserts KoreanWord data type into collection
    db_collection.insert_one(word_dict)

def delete_document(db_collection: Collection, word: str):
    """
    Delete a KoreanWord entry from the MongoDB collection by word.
    """
    db_collection.delete_one({"word": word})
    
def update_value(db_collection: Collection, word: str, key: str, value):
    """
    Update a KoreanWord entry in the collection by word and attribute name.
    """
    db_collection.update_one(
        {"word": word},           # Find the document by the 'word' field
        {"$set": {key: value}}    # Set the specified attribute to the new value
    )

def append_value(db_collection: Collection, word: str, key: str, value):
    """
    Appends an entry to an attribute of a document in a MongoDB collection.

    This function finds a document by a specified word and appends a new entry
    to a list within that document. The value to be appended is converted to a
    dictionary if it's a dataclass instance.

    Args:
        db_collection: The MongoDB collection object.
        word: The value of the 'word' field to find the document.
        key: The attribute (field) to which the new entry will be appended.
        value: The new entry to append to the list. This can be a dictionary
               or a dataclass instance.
    """
     # Check if the value is a dataclass instance and convert it to a dictionary
    # if it is. This is necessary because PyMongo cannot directly serialize
    # dataclass objects.
    if is_dataclass(value):
        value = asdict(value)

    db_collection.update_one(
        {"word": word},         # Find the document by the 'word' field
        {"$push": {key: value}} # Append the speciied attribute with new entry
    )

def set_value(db_collection: Collection, word: str, key: str, value):
    """
    Set the entry for a KoreanWord instance in the MongoDB collection.
    """
    db_collection.update_many(
        {"word": word},         # Find the document by the 'word' field
        {"$set": {
            key: value, # Set the specified attribute with the value,
            "updated_at": datetime.datetime.now() # Clock in new update to the word document
        }}
    )

    # If first instance, also set created_at value
    created = db_collection.find_one(
        {"word": word},
        {"created_at": { "exists": True }}
    )
    
    if not created:
        db_collection.update_one(
            {"word": word},
            {"$set": {"created_at": datetime.datetime.now()}}
        )

def get_value(db_collection: Collection, word: str, key: str):
    """
    Retrieve value for the specified attribute for a KoreanWord instance in the MongoDB collection
    """
    query = {"word": word}
    # Dynamically create the projection dictionary
    # This tells MongoDB to return only the requested field and exclude the _id field.
    projection = {key: 1, "_id": 0}

    document = db_collection.find_one(query, projection)

    if document:
        # Return the attribute value from the found document
        return document.get(key)
    else:
        # Return None if no value was found
        print(f"No value for '{key}' found in the document for the word: '{word}'")
        return None

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

# Tests