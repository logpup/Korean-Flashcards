from db.connection import setup_database
from db.crud import add_flashcard, get_all_flashcards

if __name__ == "__db_test__":
    flashcards_collection = setup_database()
    
    if flashcards_collection:
        try:
            # Example: Adding a new flashcard to verify the connection works.
            new_card = {"question": "What is the capital of Spain?", "answer": "Madrid"}
            result = flashcards_collection.insert_one(new_card)
            print(f"Successfully added a new flashcard with ID: {result.inserted_id}")
            
            # Example: Retrieving a card
            found_card = flashcards_collection.find_one({"question": "What is the capital of Spain?"})
            print(f"Found card: {found_card}")

        except OperationFailure as e:
            print(f"ERROR: Operation failed. {e}")
            
        finally:
            # Close the connection cleanly
            if flashcards_collection:
                flashcards_collection.database.client.close()
                print("\nDatabase connection closed.")
    else:
        print("Could not proceed with database operations due to a connection error.")
