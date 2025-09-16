import pymongo
import os
from pymongo.errors import ConnectionFailure, OperationFailure

def initialize_collection(db):
    """
    Initializes the 'korean_words' collection with specific settings for Korean.
    This includes setting up collation for proper sorting and a text index for searching.
    """
    try:
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
        db.korean_words.create_index([('word', pymongo.TEXT)], default_language='none')
        print("Text index on 'word' field created.")

        return db["korean_words"]

    except Exception as e:
        print(f"Error during collection initialization: {e}")
        return None

def setup_database():
    """
    Establishes an authenticated connection to the MongoDB server and returns the
    collection of Korean words.
    """
    MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "korean_words")
    
    if not all([MONGO_USERNAME, MONGO_PASSWORD]):
        print("ERROR: Missing MongoDB credentials in environment variables.")
        return None

    MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/?authSource=admin"
    client = None
    
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # A more modern and reliable check than 'ismaster'
        print("Successfully connected to MongoDB with authentication.")
        
        db = client[MONGO_DB_NAME]
        
        # Call the new function to set up the collection with correct settings
        collection = initialize_collection(db)
        return collection

    except ConnectionFailure as e:
        print(f"ERROR: Could not connect to MongoDB server. Please check your credentials and ensure the server is running.")
        print(f"Connection Error: {e}")
        return None
    except OperationFailure as e:
        print(f"ERROR: Authentication failed. Please check the username and password.")
        print(f"Authentication Error: {e}")
        return None

'''
if __name__ == '__test__':
    # --- Example Usage ---
    # Set your environment variables before running this script:
    # On macOS/Linux: export MONGO_USERNAME='your_user'
    #                export MONGO_PASSWORD='your_password'
    # On Windows: set MONGO_USERNAME=your_user
    #             set MONGO_PASSWORD=your_password
    
    korean_words_collection = setup_database()

    
    if korean_words_collection:
        print("\nDatabase setup complete. You can now insert data.")
        
        # Example of inserting a Korean word
        example_word = {
            "word": "안녕하세요",
            "meaning": "Hello",
            "pronunciation": "annyeonghaseyo",
            "source_url": "https://example.com"
        }
        
        try:
            korean_words_collection.insert_one(example_word)
            print(f"Inserted example word: {example_word['word']}")
        except Exception as e:
            print(f"Failed to insert example word: {e}")
'''