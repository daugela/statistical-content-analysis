#!/usr/bin/python

# -
# Take arbitrary content/text and find the most commonly occurring words.
# Form report table with results and sentences where most common words were used.
# -

from collections import Counter
import numpy as np
import pandas as pd
import glob
import sys
import re
# K-dimensional tree..
from sklearn.neighbors import KDTree

# Parabola is more accurate with decimals
import decimal

import timeit

def raw_stats(path):

    try:
        found = glob.glob(path)

    except Exception as e:
        print("Error occurred while fetching files:{}".format(e.message))
        sys.exit()

    if len(found) == 0:
        print("No files found...")
        sys.exit()

    for file in found:

        try:
            with open(file, "r") as data:
                content = data.read()
        except Exception as e:
            print("Error occurred:{}".format(e.message))
            sys.exit()

        # Remove all non alphabetical (removes dots, commas etc.)
        # Using strict a-z because of few 'φ' in Wikipedia text that results in value error..
        cleaned = re.sub('[^a-zA-Z]', ' ', content).lower()

        # List of all the words in the cleaned data
        split_it = cleaned.split()

        # Pass the split_it list to instance of Counter class.
        counter = Counter(split_it)

        # most_common() produces k frequently encountered
        # input values and their respective counts.
        most_occur = counter.most_common(10)

        print("{} {}".format(file, most_occur))


def convert2vector(word):
    # This is quite dirty here
    # I am 100% sure there's a better way without re-declaring the alphabet..
    # But this is just a proof of concept...

    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u","v", "w", "x", "y", "z"]
    vect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for char in word:
        # Put a letter count into proper index
        vect[alphabet.index(char)] = vect[alphabet.index(char)] + 1

    return np.array(vect)


def main():

    with open("content/wikipedia-philosophy.txt", "r") as data:
        content = data.read()

    # Remove all non alphabetical (removes dots, commas etc.)
    # Using strict a-z because of few 'φ' in Wikipedia text that results in value error..

    cleaned = re.sub('[^a-zA-Z]', ' ', content).lower()

    # split() returns list of all the words in the string
    split_it = cleaned.split()

    raw_list_of_vectors = []

    for word in split_it:
        raw_list_of_vectors.append(convert2vector(word))
        #raw_list_of_vectors = np.append(raw_list_of_vectors, convert2vector(word))

    raw_list_of_vectors = np.array(raw_list_of_vectors)

    dataset_vector_tree = KDTree(raw_list_of_vectors, leaf_size=26)

    word = "philosophy"

    # Explanation:
    # This should be small to none for short words and dynamically adjusted into bigger numbers
    # Increase should be accelerated so probably best defined with a bit sketched parabolic function
    # For exact word "philosophy" (10 characters) from wikipedia - 2.4 founds best results (including mistype!)
    # 2.5 already allows similar "PSYchology" to creep into resultset from same Wikipedia article:)
    # I am using this point to interpolate backwards to 2 characters and forwards to infinity
    # Approximate parabola that fits the "philosophy" numbers - is 0.024x^2
    # Graph in https://www.desmos.com/calculator/dz0kvw0qjg or README

    tolerance = decimal.Decimal("0.024") * decimal.Decimal(len(word) ** 2)

    counts = dataset_vector_tree.query_radius([convert2vector("philosophy")], tolerance, count_only=False)

    for match in counts[0]:
        print(split_it[match])

    # print(dataset_vector_tree.query_radius(raw_list_of_vectors[6], r=1, count_only=True))
    # print(len(raw_list_of_vectors))
    # print('shape of tree is ', dataset_vector_tree.data)
    # nearest = dataset_vector_tree.query(convert2vector("philosophy"), k=1, distance_upper_bound=9)

    #vect = convert2vector("philosophy")
    # res = dataset_vector_tree.query_radius(vect, r=1.5, count_only=True)
    #print(res)



    # print(nearest)

    # Pass the split_it list to instance of Counter class.
    # counter = Counter(split_it)

    # most_common() produces k frequently encountered
    # input values and their respective counts.
    #most_occur = counter.most_common(10)

    #print("{} {}".format("content/advanced.txt", most_occur))

    #sentence = {'Word(#)': ['Word1', 'Word2', 'Word3', 'Word4', 'Word5'],
    #             'Documents': ['doc1.txt', 'doc1.txt', 'doc1.txt', 'doc1.txt', 'doc1.txt'],
    #             'Sentences containing the word': ['Let me begin by sa today.', 'Word2', 'Word3', 'Word4', 'Word5']
    #            }

    #df = pd.DataFrame(sentence, columns=['Word(#)', 'Documents', 'Sentences containing the word'])

    # Setup DataFrame to print whole data without (default) truncation after 50 chars
    #pd.set_option('display.max_colwidth', -1)

    # Print DataFrame table without first column with indexes (a bit confusing if present)
    #print(df.to_string(index=False))


if __name__ == "__main__":

    path = "content/*.txt"
    raw_stats(path)
    main()
