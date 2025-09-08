import pandas as pd
import os

def export_flashcard_data(dataframe: pd.DataFrame, filename: str, separator: str = ','):
    _export_to_quizlet(dataframe, filename, separator)
        
def _export_to_quizlet(dataframe: pd.DataFrame, filename: str, separator: str = ','):
    """
    Exports a Pandas DataFrame to a text file.

    Args:
        dataframe (pd.DataFrame): The DataFrame to export.
        filename (str): The desired name of the output text file.
                        This should include the file extension, e.g., 'output.txt'.
        separator (str): The delimiter to use between columns in the output file.
                         Common choices are ',' (for CSV) or a tab '\t'.
    """
    try:
        # Use the to_csv method to write the DataFrame to the text file.
        # index=False prevents pandas from writing the DataFrame index as a column.
        # We use a try-except block to handle potential file writing errors.
        dataframe.to_csv(filename, index=False, sep=separator)
        print(f"Successfully exported DataFrame to '{filename}'")
    except Exception as e:
        print(f"An error occurred while exporting the DataFrame: {e}")