#!/usr/bin/python

# -
# Take arbitrary content/text and find the most commonly occurring words.
# Form report table with results and sentences where most common words were used.
# -

import decimal  # Parabola is more accurate with decimals
import glob
import numpy as np
import nltk
import pandas as pd
import re
import sys

from collections import Counter
from sklearn.neighbors import KDTree


def fetch_file_content(file):

    try:
        with open(file, "r") as data:
            content = data.read()
    except Exception as e:
        print("Error occurred:{}".format(e.message))
        sys.exit()

    # Remove all non alphabetical (removes dots, commas etc.)
    # Using strict a-z (instead of \W) because of few 'φ' in Wikipedia text that results in value error..
    cleaned = re.sub('[^a-zA-Z]', ' ', content).lower()

    # List of all the words in the cleaned data
    content_list = cleaned.split()
    return content_list


def stats_raw(path):

    try:
        found = glob.glob(path)

    except Exception as e:
        print("Error occurred while fetching files:{}".format(e.message))
        sys.exit()

    if len(found) == 0:
        print("No files found at {}".format(path))
        sys.exit()

    for file in found:

        content_list = fetch_file_content(file)

        # Pass the split_it list to instance of Counter class.
        dataset_counter = Counter(content_list)

        # most_common() produces k frequently encountered
        # input values and their respective counts.
        most_occur = dataset_counter.most_common(10)

        print("{} {}".format(file, most_occur))


# For the purpose of this example with wiki - we need to add a target word param
# This might be extended into some search functionality in the future instead of some raw stats
def stats_advanced(path, query):

    try:
        found = glob.glob(path)

    except Exception as e:
        print("Error occurred while fetching files:{}".format(e.message))
        sys.exit()

    if len(found) == 0:
        print("No files found at {}".format(path))
        sys.exit()

    for file in found:

        content_list = fetch_file_content(file)

        raw_list_of_vectors = []

        for word in content_list:
            raw_list_of_vectors.append(convert2vector(word))

        raw_list_of_vectors = np.array(raw_list_of_vectors)

        dataset_vector_tree = KDTree(raw_list_of_vectors, leaf_size=26)

        # Explanation:
        # This should be small to none for short words and dynamically adjusted into bigger numbers
        # Increase should be accelerated so probably best defined with a bit sketched parabolic function
        # For exact word "philosophy" (10 characters) from wikipedia - 2.4 founds best results (including mistype!)
        # 2.5 already allows similar "PSYchology" to creep into resultset from same Wikipedia article:)
        # I am using this point to interpolate backwards to 2 characters and forwards to infinity
        # Approximate parabola that fits the "philosophy" numbers - is 0.024x^2

        tolerance = decimal.Decimal("0.024") * decimal.Decimal(len(query) ** 2)

        counts = dataset_vector_tree.query_radius([convert2vector(query)], tolerance, count_only=False)

        results = []
        for match in counts[0]:
            # print(content_list[match])
            results.append(content_list[match])

        # draw_results accepts simple list (convert back from np array)

        draw_results(results, file)


def convert2vector(word):
    # Just a proof of concept - quite dirty here
    # I am 100% sure there's a better way without re-declaring the alphabet..

    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u","v", "w", "x", "y", "z"]
    vect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for char in word:
        # Put a letter count into proper index
        vect[alphabet.index(char)] = vect[alphabet.index(char)] + 1

    return np.array(vect)


def draw_results(matches, file):

    # Remove duplicates and join into one string with commas
    matches_unique = ", ".join(set(matches))

    try:
        with open(file, "r") as data:
            content = data.read()
    except Exception as e:
        print("Error occurred:{}".format(e.message))
        sys.exit()

    # In this implementation I only use nltk to extract sentences from content file
    # Language should probably be detected from content before selecting a tokenizer
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    # All sentences in the file
    sentences_list = tokenizer.tokenize(content)

    # Loop sentences to find containing our query
    # This one is also quite dirty
    # Probably would be nicer with some lambda function or similar

    sentences_match = []

    for sentence in sentences_list:
        for query in matches_unique:
            if query in sentence.lower():
                sentences_match.append(sentence)
                break

    print("Total of {} advanced matches found".format(len(matches)))

    # Use DataFrame to display results
    data = {'Words(#)': [matches_unique], 'Documents': [file], 'Sentences containing the word': [str(len(sentences_match))]}

    df = pd.DataFrame(data, columns=['Words(#)', 'Documents', 'Sentences containing the word'])

    # Setup DataFrame to print whole data without (default) truncation after 50 chars
    pd.set_option('display.max_colwidth', -1)

    # Print DataFrame table without first column with indexes (a bit confusing if present)
    print(df.to_string(index=False))


def main():

    print("\nRAW stats (exact matches):\n")
    stats_raw("content/*.txt")
    print("\nAdvanced analytics:\n")
    stats_advanced("content/wikipedia-philosophy.txt", "philosophy")


if __name__ == "__main__":
    main()


