import pandas as pd

# Create a list of vocabulary words with definitions and example sentences
data = {
    "Korean Word": [],
    "Hanja"
    "English Definition": [],
    "Example Sentence": []
}

# Create a DataFrame
df = pd.DataFrame(data)

# Method to adda new entry to the DataFrame
def add_flashcard_entry(df, word, definition, example_sentence):
    new_entry = {
        "Word": word,
        "Definition": definition,
        "Example Sentence": example_sentence
    }
    #Append the new entry to the Data Frame and return the updated DataFrame
    df = df.append(new_entry, ignore_index=True)
    return df

# Display the table
print(df)