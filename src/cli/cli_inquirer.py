from InquirerPy import inquirer, prompt
from InquirerPy.exceptions import InvalidArgument
    
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