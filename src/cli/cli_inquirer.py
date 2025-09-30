from typing import List

from InquirerPy import inquirer, prompt
from InquirerPy.exceptions import InvalidArgument

async def select_words(word_list: List) -> List:
    """
    Ask user to select words from a list
    """
    try:
        result_list = await inquirer.checkbox(
                message="These words are already in the database. Select which entries you would still want to include for this deck.\n[Space] to Select\n[Enter] to Confirm Entry",
                choices=word_list,
            ).execute_async()
        return result_list
    
    except InvalidArgument as e:
        print(f"Error creating prompt: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during the prompt: {e}")
        return False

async def ask_to_aggregate_data():
    """
    Ask user if they want to aggregate data again
    """
    try:
        result = await inquirer.confirm(
            message="Would you like to aggregate data once again?",
            default=False,  # Suggest "no" as the default answer
        ).execute_async()
        
        # inquirer.confirm returns a boolean directly, no need to index
        return result
        
    except InvalidArgument as e:
        print(f"Error creating prompt: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during the prompt: {e}")
        return False