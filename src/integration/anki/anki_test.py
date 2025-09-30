from db.connection import connect_server, retrieve_collection
from anki.card_generator import create_anki_card, create_anki_deck
from logic.logic_processor import query_anki_flashcard_data

client = connect_server()
collection = retrieve_collection(client)

word_list = ["만족", "가을", "인정"]

deck_data = []

for korean_word in word_list:
    print(f"{korean_word}")
    word_data = query_anki_flashcard_data(collection, korean_word)
    note = create_anki_card(word_data)
    deck_data.append(note)

deck_name = "test"
output_filepath = "./tests/test.apkg"
create_anki_deck(deck_name, deck_data, output_filepath)