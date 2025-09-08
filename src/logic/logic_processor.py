import pandas as pd

from logic.logic_lookup import lookup_entry

def populate_flaschard_data(df):
    """
    Populates a pandas DataFrame with Hanja, English definition, and an example
    sentence for a list of Korean words in the first column.

    Args:
        df (pd.DataFrame): A DataFrame with Korean words in the first column.

    Returns:
        pd.DataFrame: The original DataFrame with three new columns populated
                      with Hanja, English definition, and example sentences.
    """
    if df.empty or df.shape[1] < 1:
        print("Input DataFrame is empty or does not have a first column.")
        return df
    
    # Add new columns to the DataFrame
    df['Hanja'] = ""
    df['English Definition'] = ""
    df['Example Sentence'] = ""

    # Iterate through the rows of the DataFrame
    for index, row in df.iterrows():
        korean_word = row[0] # Assuming the Korean word is in the first column

        # Retrieve data from the lookup function
        word_entry = lookup_entry(korean_word)
        hanja = word_entry['hanja']
        english = word_entry['english_definition']
        example = word_entry['example_sentence']

        # Populate the new columns
        df.at[index, 'Hanja'] = hanja
        df.at[index, 'English Definition'] = english
        df.at[index, 'Example Sentence'] = example

    return df
