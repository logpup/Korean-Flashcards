import pandas as pd
import os

def import_candidate_file(filepath):
    """
    Imports Korean words from a variety of file types.
    
    Args:
        filepath (str): The path to the file containing the word list.
        
    Returns:
        pd.DataFrame: A DataFrame with 'korean_word' and 'english_definition' columns,
                      or an empty DataFrame if the file type is not supported or an error occurs.
    """
    file_extension = os.path.splitext(filepath)[1].lower()

    if file_extension == '.txt':
        return _import_txt(filepath)
    elif file_extension == '.html':
        return _import_html(filepath)
    else:
        print(f"❌ Error: Unsupported file type: {file_extension}")
        return pd.DataFrame()

def _import_txt(filepath):
    """
    Internal function to import a simple text file.

    The moethod performs the following steps;
    1. Opens and reads the specified text file.
    2. Strips leading/trailing whitespaces and removes linebreak from each line.
    3. Filters out any empty lines.
    4. Create a pandas DataFrame where the cleaned lines are stored in the first column.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip().split(',', 1) for line in f if line.strip()]
            df = pd.DataFrame(lines, columns=['korean_word'])
            return df
    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error importing TXT: {e}")
        return pd.DataFrame()

def _import_html(filepath):
    """
    Reads a local HTML file, removes linebreaks, and stores the contents of
    each line in a pandas DataFrame.

    The method performs the following steps:
    1. Opens and reads the specified HTML file.
    2. Strips leading/trailing whitespace and removes linebreaks from each line.
    3. Filters out any empty lines.
    4. Creates a pandas DataFrame where the cleaned lines are stored in the
       first column.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Create a DataFrame from the list of lines
        df = pd.DataFrame(lines, columns=['line_content'])
        
        return df
    
    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error importing HTML: {e}")
        return pd.DataFrame()