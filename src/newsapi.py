# This script prepares raw BBC news text → structured dataset with extracted countries, 
# cities, and nationalities for downstream analysis.

# import important libraries 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import spacy

import pycountry
import geonamescache


df_bbc = pd.read_csv('../dataset/bbc_news.csv')
# df_bbc.head()

# drop title duplicates
df_bbc = df_bbc.drop_duplicates(subset='title')


# combine for title and text values for feature
df_bbc['text'] = df_bbc['title'] + ' ' + df_bbc['description']



# determine length of word
df_bbc['word_in_description'] = df_bbc['text'].str.split().str.len()



# df_bbc.head(2)


# NLP Processing 
nlp = spacy.load("en_core_web_sm")

from spacy.lang.en.stop_words import STOP_WORDS

stopwords = list(STOP_WORDS)



test = df_bbc['text'][0]
doc = nlp(test)
print(doc.text)

for ent in doc.ents:
    if ent.label_ == "NORP":
        print(ent.text, "->", ent.label_)


# def preprocessing(text):
#     stopwords = set(STOP_WORDS)  # build once for O(1) lookup
#     exclude_pos = {"PUNCT", "SYM", "SPACE"}  # predefine excluded POS
#     doc = nlp(text)
#     clean_tokens = [
#         token.lemma_.lower()
#         for token in doc
#         if token.text.lower() not in stopwords and token.pos_ not in exclude_pos
#     ]
#     return " ".join(clean_tokens)


# Normalize everything to lowercase once
abbrev_countries = {c.lower() for c in {
    "USA", "UK", "UAE", "DRC", "ROC", "China", "Russia", 
    "S. Korea", "South Korea", "N. Korea", "North Korea", 
    "Ivory Coast", "Syria", "Palestine", "Holland", "Burma", 
    "Zaire", "Kosovo", "Hong Kong", "Macau", "Scotland", 
    "Wales", "England", "Northern Ireland", "Taiwan"
}}

# Mapping for standardization
abbrev_map = {
    "us": "United States",
    "usa": "United States",
    "uk": "United Kingdom",
    "uae": "United Arab Emirates",
    "dr congo": "Congo, The Democratic Republic of the",
    "congo": "Congo, The Democratic Republic of the",
    "roc": "Taiwan",
    "ivory coast": "Côte d'Ivoire",
    "holland": "Netherlands",
    "burma": "Myanmar",
    # "zaire": "Congo, The Democratic Republic of the",
    "palestine": "Palestine, State of",
    "kosovo": "Kosovo",
    "hong kong": "Hong Kong",
    "macau": "Macao",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "england": "United Kingdom",
    "northern ireland": "United Kingdom",
    "taiwan": "Taiwan"
}

# Set of all official ISO-recognized country names (normalized to lowercase)
official_countries = {c.name.lower() for c in pycountry.countries}

def get_countries(text):
    """
    Extract countries from a given text using spaCy NER + pycountry.
    
    Args:
        text (str): Input text to analyze.
    
    Returns:
        list: Unique list of country names or abbreviations mentioned in the text.
    
    Process:
    1. Run spaCy's NLP pipeline on the text.
    2. Collect named entities labeled as 'GPE' (Geo-Political Entity).
    3. Keep only those that match official countries or known abbreviations.
    4. Return a unique list of matches (case-insensitive).
    """
    # Process text with spaCy model
    doc = nlp(text)
    results = set()

    for ent in doc.ents:
        if ent.label_ == "GPE":
            candidate = ent.text.strip()

            # Normalize lowercase for dictionary matching
            candidate_lower = candidate.lower()

            # Case-sensitive handling for "US" which means 'United States'
            if candidate == "US":
                results.add("United States")
            elif candidate_lower in official_countries:
                results.add(ent.text.strip())
            elif candidate_lower in abbrev_countries:
                results.add(abbrev_map.get(candidate_lower, candidate))
    
    return list(results)



# get nationalities
def get_nationalities(text):
    doc = nlp(text) # Process text with spaCy model
    
    return list({
        ent.text.lower().strip()
        for ent in doc.ents
        if ent.label_ == "NORP"
    })



# Initialize geonamescache
gc = geonamescache.GeonamesCache()

# Precompute a set of all city names (lowercased) for fast membership lookup
# Using a set makes "is this a city?" checks O(1) instead of O(n).
all_cities = {city['name'].lower() for city in gc.get_cities().values()}  # precompute once

def get_cities(text):
    """
    Extract cities from a given text using spaCy NER + geonamescache lookup.

    Args:
        text (str): Input text to analyze.

    Returns:
        list: List of detected city names (lowercased) found in the text.

    Process:
    1. Run spaCy's NLP pipeline on the text.
    2. Collect named entities from spaCy.
    3. Check if the entity text matches a known city in geonamescache.
    4. Return a list of all matches (duplicates may occur if cities repeat).
    """
    # run through spacy model 
    doc = nlp(text)
    # Collect entities that match known city names
    return [ent.text.lower() for ent in doc.ents if ent.text.lower() in all_cities]
        





# df_bbc['processed_desc'] = df_bbc['text'].map(preprocessing)


# extract countries 
df_bbc['countries'] = df_bbc['text'].map(get_countries)


# extract nationalities / ideologies 
df_bbc['nationalities'] = df_bbc['text'].map(get_nationalities)


# extract cities 
df_bbc['cities'] = df_bbc['text'].map(get_cities)


# remove empty sets 
df_bbc['countries'] = df_bbc['countries'].apply(lambda x: str(x) if x else '' )
df_bbc['nationalities'] = df_bbc['nationalities'].apply(lambda x: str(x) if x else '' )
df_bbc['cities'] = df_bbc['cities'].apply(lambda x: str(x) if x else '' )


# df_bbc = df_bbc[['text', 'processed_desc', 'countries', 'nationalities', 'cities' ]]
df_bbc = df_bbc[['text', 'countries', 'nationalities', 'cities' ]]



# Standardize messy text/list columns into clean Python lists, 
cols_to_split = ['countries', 'nationalities', 'cities']

def safe_split(x):
    if pd.isna(x):               # None/NaN → empty list
        return []
    if isinstance(x, list):      # already list → leave it
        return x
    if isinstance(x, str):       # split string by comma
        return [i.strip() for i in x.split(",") if i.strip() != ""]
    return []

for col in cols_to_split:
    df_bbc[col] = df_bbc[col].apply(safe_split)



# ​​Function to pad lists to the same length by replacing with Null Values
def pad_lists(row):
    max_len = max(len(row['countries']), len(row['nationalities']), len(row['cities']))
    row['countries'] += [None] * (max_len - len(row['countries']))
    row['nationalities'] += [None] * (max_len - len(row['nationalities']))
    row['cities'] += [None] * (max_len - len(row['cities']))
    return row

# Apply the padding function to each row
df_bbc = df_bbc.apply(pad_lists, axis=1)

# Now, safely explode both columns
df_bbc = df_bbc.explode(['countries','nationalities', 'cities'])


df_bbc.countries = df_bbc.countries.str.replace("[", "").str.replace("]", "").str.replace("'", "").str.replace(",", "")
df_bbc.nationalities = df_bbc.nationalities.str.replace("[", "").str.replace("]", "").str.replace("'", "").str.replace(",", "")
df_bbc.cities = df_bbc.cities.str.replace("[", "").str.replace("]", "").str.replace("'", "").str.replace(",", "")



df_bbc.fillna("", inplace=True)


# capitalize nationality values for better exploration
df_bbc.nationalities = df_bbc.nationalities.str.capitalize()
df_bbc.cities = df_bbc.cities.str.capitalize()


df_bbc.countries.value_counts()


df_bbc.replace('USA', 'United States', inplace=True)


df_bbc.to_csv('../dataset/new_data.csv', index=False)





