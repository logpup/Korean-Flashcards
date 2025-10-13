# Standard Python library imports
from typing import List, Dict, Tuple

# Third-party external library imports
from pymongo.collection import Collection
from InquirerPy import inquirer, prompt
from InquirerPy.validator import EmptyInputValidator
from InquirerPy.exceptions import InvalidArgument

# Internal Library Imports
from logic.logic_processor import process_user_entry

async def select_words(word_list: List, prompt_message: str) -> Tuple[List, List]:
    """
    Ask user to select words from a list
    """
    try:
        selected_words = await inquirer.checkbox(
                message=prompt_message,
                choices=word_list,
            ).execute_async()
        
         # Convert selected_words to a set for fast O(1) lookups
        selected_set = set(selected_words)
        # Use a list comprehension to build the list of unselected words
        unselected_words = [
            word for word in word_list if word not in selected_set
        ]

        # Return both the selected and unselected lists
        return selected_words, unselected_words
    
    except InvalidArgument as e:
        print(f"Error creating prompt: {e}")
        return [], []
    except Exception as e:
        print(f"An unexpected error occurred during the prompt: {e}")
        return [], []

async def ask_to_aggregate_data():
    """
    Ask user if they want to aggregate data again
    """
    try:
        result = await inquirer.confirm(
            message="Would you like to aggregate data once again?",
            default=False,
        ).execute_async()
        
        return result
        
    except InvalidArgument as e:
        print(f"Error creating prompt: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during the prompt: {e}")
        return False

async def collect_senses_data() -> List:
    senses = []
    sense_idx = 1

    # Initialize variable to control loop
    continue_prompt = True

    while True:
        # Ask to add another sense
        if sense_idx > 1:
            continue_prompt = await inquirer.confirm(
                message=f"    → Add Sense #{sense_idx} for this entry?"
            ).execute_async()

        if not continue_prompt:
            break

        # Prompt for a sense
        definition = await inquirer.text(
            message=f"      Sense #{sense_idx} Definition:",
            validate=EmptyInputValidator(),
            filter=lambda x: x.strip()
        ).execute_async()

        # 1.b. Part of Speech (List selection, required)
        pos = await inquirer.select(
            message="  Select Part of Speech:",
            choices=["명사", "대명사", "수사", "동사", "형용사", "관형사", "부사", "조사", "감탄사"],
        ).execute_async()

        # Initialize varaible pos_str
        pos_str = ""
        if pos:
            pos_str = f"[{pos}] "
        sense = f"{pos_str}{definition}"

        # Append to list of senses
        senses.append(sense)
        sense_idx += 1

    if senses:
        return senses
    else:
        return []

async def collect_hanja_idiom_pairs_data() -> Dict:
    entries = []
    entry_idx = 1

    while True:
        print(f"\n--- Word Entry #{entry_idx} ---")
        
        # 1. Ask to continue/stop
        add_entry = await inquirer.confirm(
            message=f"Add Word Entry #{entry_idx} (Hanja, POS, Senses)?"
        ).execute_async()
        
        if not add_entry:
            break
            
        # 1.a. Hanja (Optional)
        hanja = await inquirer.text(
            message="  Enter the Hanja character (optional):",
            filter=lambda x: x.strip()
        ).execute_async()
        
        # 1.c. Collect all Senses for this specific entry (Nested loop)
        senses = await collect_senses_data()

        # Append the combined data as a single dictionary
        entries.append({
            "hanja": hanja if hanja else None,
            "senses": senses,
        })
        entry_idx += 1
        
    return entries

async def collect_en_examples_data() -> List[Dict[str,str]]:
    en_examples = []
    en_example_idx = 1

    while True:
        # Ask to add another example pair
        continue_example = await inquirer.confirm(
            message=f"\nAdd Example Sentence Pair #{en_example_idx}?"
        ).execute_async()
        
        if not continue_example:
            break
        
        # Prompt 2.a: Korean Sentence (Required)
        korean_sentence = await inquirer.text(
            message=f"  Example #{en_example_idx} Korean Sentence:",
            validate=EmptyInputValidator(),
            filter=lambda x: x.strip()
        ).execute_async()

        # Prompt 2.b: English Sentence (Required)
        english_sentence = await inquirer.text(
            message=f"  Example #{en_example_idx} English Sentence:",
            validate=EmptyInputValidator(),
            filter=lambda x: x.strip()
        ).execute_async()
        
        en_examples.append({
            "korean_sentence": korean_sentence,
            "english_sentence": english_sentence
        })
        en_example_idx += 1

        # Add this return statement:
        return en_examples
        
async def input_user_word_data(collection: Collection, word_info: Dict):
    """
    Prompt user to enter data for a specified word
    1. Have user enter entries (loop through as many wanted)
        a. hanja
        b. part of speech
        c. senses (loop through as many wanted)
    2. Have user enter examples (loop through as many wanted)
        a. korean sentence
        b. english sentence
    3. Save informtion as a dictionary, and send to database
    """
    korean_word = word_info["korean_word"]
    missing_values = word_info["missing_values"]

    # Initialize variable to hold page data
    page_data = {
        "korean_word": korean_word,
        "hanja_idiom_pairs": [],
        "en_examples": [],
    }

    # 1. Collect word entries if a missing value
    if "entries" in missing_values:
        user_hanja_idiom_pairs_data = await collect_hanja_idiom_pairs_data()

        for entry in user_hanja_idiom_pairs_data:
            page_data["hanja_idiom_pairs"].append(entry)
    
    # 2. Collect English examples if a missing value
    if "examples" in missing_values:
        user_en_examples_data = await collect_en_examples_data()

        for en_example in user_en_examples_data:
            page_data["en_examples"].append(en_example)
    
    # 3. Save information to the database
    process_user_entry(collection, korean_word, page_data)


    


    



    
