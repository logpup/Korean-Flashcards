import pymongo
import os
from pymongo.errors import ConnectionFailure, OperationFailure

def setup_database():
    """
    Establishes an authenticated connection to the MongoDB server and returns the
    flashcards collection. This is a more secure way to connect to a database.

    Returns:
        The MongoDB collection object if the connection is successful, None otherwise.
    """
    # Read credentials from environment variables for security.
    MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "korean_flashcards_project")
    
    if not all([MONGO_USERNAME, MONGO_PASSWORD]):
        print("ERROR: Missing MongoDB credentials in environment variables.")
        return None

    # Connection string format for authentication. authSource is the database where
    # the user was created (e.g., 'admin' is common).
    # Replace the host and port if your database is not local.
    MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/?authSource=admin"

    client = None
    try:
        # Connect to the MongoDB server with a timeout to avoid hanging.
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # The ismaster command is a simple check to confirm a successful connection.
        client.admin.command('ismaster')
        print("Successfully connected to MongoDB with authentication.")
        
        # Access the specified database and collection.
        db = client[MONGO_DB_NAME]
        collection = db["korean_flashcards"]
        print(f"Database '{MONGO_DB_NAME}' and collection 'korean_flashcards' initialized.")

        return collection

    except ConnectionFailure as e:
        print(f"ERROR: Could not connect to MongoDB server. Please check your credentials and ensure the server is running.")
        print(f"Connection Error: {e}")
        return None
    except OperationFailure as e:
        print(f"ERROR: Authentication failed. Please check the username and password.")
        print(f"Authentication Error: {e}")
        return None