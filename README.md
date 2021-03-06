### Task
In the attached documents, find the most commonly occurring words and the sentences where they are used to create the following table:


| Word(#)  | Documents | Sentences containing the word    |
| -------- | --------- | -------------------------------- |
| philosophy | x, y, z | I don't have time for **philosophy** |



This is an example, you have the flexibility to modify the final output display as per your wish.  
Idea behind it is to build a reusable solution which can be extended to other documents and text sources.  
This is an opportunity to display your engineering flair.  
We highly encourage you to showcase your engineering ability rather than only fulfilling the requirements of the task.  


### My assumption:

Raw stats (exact match word frequencies) of provided docs is ~the same:

```
doc1.txt [('the', 119), ('and', 103), ('to', 93), ('that', 85), ('of', 75), ('a', 62), ('we', 61), ('s', 47), ('in', 44), ('i', 43)]
doc2.txt [('the', 211), ('and', 181), ('to', 135), ('that', 127), ('of', 113), ('a', 87), ('i', 81), ('we', 77), ('in', 70), ('for', 62)]
doc3.txt [('the', 139), ('and', 132), ('to', 89), ('that', 83), ('we', 77), ('a', 65), ('of', 60), ('i', 56), ('in', 52), ('our', 43)]
doc4.txt [('the', 173), ('and', 125), ('of', 117), ('to', 94), ('a', 76), ('that', 76), ('in', 61), ('is', 46), ('it', 36), ('i', 32)]
doc5.txt [('the', 214), ('to', 157), ('and', 156), ('of', 126), ('a', 118), ('in', 110), ('that', 99), ('we', 63), ('our', 61), ('is', 60)]
doc6.txt [('the', 106), ('to', 77), ('and', 76), ('of', 49), ('in', 46), ('we', 45), ('a', 34), ('that', 33), ('this', 23), ('is', 23)]
```

This basically follows general (known) results of basic English language with [the, and, to] being on top.  
So I assume I need to try some more interesting approach:)  

### Adding philosophy:

Task description has some philosophy in it. Let's fetch article about it from Wikipedia and use this as additional (more interesting) content input.  
Same raw stats returns word 'philosophy' on top (**only 14 matches**) and than the same pattern of [and, of, the] remains:

```
content/wikipedia-philosophy.txt [('philosophy', 14), ('of', 14), ('and', 14), ('the', 9), ('to', 8), ('is', 7), ('as', 6), ('or', 6), ('a', 5), ('for', 4)]
```

But this is the problem, because these are exact matches and there's more variations!

### My basic idea:

- This is a **proof of concept**
- Use collections module for ease of word extraction and structuring of raw docs input data.  
- Convert all input words into easily comparable **lowercase** vectors of 26 length:  

  0001001000200100000000000 == hello  
  abcdefghijklmnopqrstuvwxyz  


| 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | =hello |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|--------|
| a | b | c | d | **e** | f | g | **h** | i | j | k | **l** | m | n | **o** | p | q | r | s | t | u | v | w | x | y | z |        |


- Shrink dataset combining partial word matches (similar syntax expressions, lingual forms or plain mistypes) using [scikit-learn's](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html) K-dimensional tree  
  For example:  
  promise ~== promises  
  watch ~== watching  
  philosophy ~== philosophical  

- Think of the way to determine some more dynamic leveling of difference tolerance between word matches.
  Nouns, verbs and various word |lengths| ~might need different levels of tolerance to be interpreted as "the same".
  So I will use [query_radius](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html#sklearn.neighbors.KDTree.query_radius) method with variant radius (tolerance) to fetch ~similar matches from dataset.
  Shorter words will have much smaller (minor to non-existent) acceptable variant because
  this increases false positives with too little vector params for words like: "and", "do", "like" etc...
  I have chosen parabola with initial point (10, 2.4) as a reference (explanation below)

- Use [nltk](http://www.nltk.org/data.html) to extract sentences from source file and display matching results

### Graph explanation of difference tolerance parameter for words of different lengths (characters)

This should be small to none for short words and dynamically adjusted into bigger numbers  
Increase should not be linear so probably best defined with a bit sketched parabolic function  
For our exercise exact word "philosophy" (10 characters) from wikipedia - **2.4** happens to find best results:
21 matches including one mistype (on purpose) of the same word: 


```
Advanced analytics:

Total of 21 advanced matches found
Words(#)                                                                                     Documents                         Sentences containing the word
philosophia, philosopher, philosophy, phylosophy, philosophical, philosophies, philosophers  content/wikipedia-philosophy.txt  24  
```

**2.5** already allows similar "PSYchology" to creep into resultset from same Wikipedia article:)
I am using this as a starting point to interpolate backwards to 2 characters and forwards to ~20 which is enough for most "normal human" words.
Approximate parabola that fits the "philosophy" numbers - is **0.024x^2**
Graph in https://www.desmos.com/calculator/dz0kvw0qjg
This is a proof of concept but function ~should be similar in slope for other words too (of similar lengths/tolerance)

![Alt text](tolerance_parabola.png?raw=true "Parabolic dependency of vector tolerance vs. word length")
 
### Further improvement & ideas:  
- Different words might have different torelance values before mismatches occur.
- convert2vector is kinda one-way transformation that needs to be binded into raw data to keep context.
  Just because same letter combination could some time result into different word (sequence matters)
  This is especially dangerous for short words.
- Language should probably be detected before extracting sentences from input files
 
### Running
Clone this repo  
Enable virtual env  
```
pip install -r requirements.txt
```

Run analyze.py
```
python analyze.py
```
