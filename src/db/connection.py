import os
import urllib.parse
import pymongo
from pymongo.errors import ConnectionFailure, OperationFailure

def connect_to_server():
    """
    Establishes an authenticated connection to the MongoDB server. Uses environment
    variables for credential for security.

    Returns:
        client (pymongo.MongoClient): Represents a direct, authenticated connection to your
            MongoDB server. You can think of it as the main entry point for all your
            database operations.
    """
    # Retrieve python environment variables for MongoDB user authentication
    raw_username = os.environ.get("MONGO_USERNAME")
    raw_password = os.environ.get("MONGO_PASSWORD")

    if not all([raw_username, raw_password]):
        print("ERROR: Missing MongoDB credentials in environment variables.")
        return None
    
    # Encode strings retrieved from the environment vairables for url parsing
    MONGO_USERNAME = urllib.parse.quote_plus(raw_username)
    MONGO_PASSWORD = urllib.parse.quote_plus(raw_password)
    
    # Set Mongo URI with the variables encoded in the previous step
    MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/?authSource=korean_words"
    client = None
    
    # Connect to the MongoDB server
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # A more modern and reliable check than 'ismaster'
        print("Successfully connected to MongoDB with authentication.")

        return client

    except ConnectionFailure as e:
        print(f"ERROR: Could not connect to MongoDB server. Please check your credentials and ensure the server is running.")
        print(f"Connection Error: {e}")
        return None
    except OperationFailure as e:
        print(f"ERROR: Authentication failed. Please check the username and password.")
        print(f"Authentication Error: {e}")
        return None

def initialize_collection(client):
    """
    Initializes a new MongoDB collection tailored for Korean language data

    Args:
        client (pymongo.MongoClient): Represents a direct, authenticated connection to your
            MongoDB server. You can think of it as the main entry point for all your
            database operations.
    
    Returns:
        collection: A collection in a database which serves as logical container for a group
            of documents.
    """
    # Retrieve name of the database set as a Python environment variable
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "korean_words")

    if not ([MONGO_DB_NAME]):
        print("ERROR: Missing MongoDB NAME in environment variables.")
        return None

    try:
        db = client[MONGO_DB_NAME]

        # Check if the 'korean_words' collection already exists to avoid re-creation errors.
        if "korean_words" in db.list_collection_names():
            print("Collection 'korean_words' already exists. Skipping initialization.")
            return db["korean_words"]

        # Create the collection with Korean collation.
        # 'ko' is the locale code for Korean.
        # 'strength': 2 ensures that sorting handles character variations correctly.
        db.create_collection("korean_words", collation={'locale': 'ko', 'strength': 2})
        print("Collection 'korean_words' created with Korean collation.")

        # Create a text index on the 'word' field for efficient text search.
        # 'default_language: none' is crucial here. It prevents MongoDB from
        # applying any stemming rules, which it lacks for Korean.
        db.korean_words.create_index([('word', pymongo.ASCENDING)])
        print("Standard index on 'word' field created with collation.")

        collection = db["korean_words"]

        return collection

    except Exception as e:
        print(f"Error during collection initialization: {e}")
        return None