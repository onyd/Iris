from gensim.models import Word2Vec, KeyedVectors
import re
import os
from gensim import utils
import spacy
import time
import xml.etree.ElementTree as ET
from lxml import etree

from Iris.utils.DataProcessing.DataBuilder import DataBuilder
nlp = spacy.load("fr_core_news_md", disable=['ner', 'tagger', 'parser'])
sentencizer = nlp.create_pipe("sentencizer")
nlp.add_pipe(sentencizer)


def find_paths(path):
    paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                paths.append(os.path.join(root, file))

    return paths


class XMLCorpus:
    def __init__(self, path, tag):
        self.path = path
        self.tag = tag

    def __iter__(self):
        i = 0
        t = time.time()
        for event, elem in etree.iterparse(self.path,
                                           events=('start', 'end'),
                                           encoding="utf-8",
                                           recover=True):
            if event == 'end':
                doc = nlp(elem.text)
                sents = [sent for sent in doc.sents]
                for sent in sents:
                    doc = nlp(sent.text)
                    yield [token.lemma_ for token in doc]

                # Print info
                i += 1
                if i % 10000 == 0:
                    print("Processed {} elements after {} min".format(
                        i, int(((time.time() - t) / 60))))


class MyCorpus:
    """An interator that yields sentences (lists of str)."""
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        i = 0
        t = time.time()
        with open(self.path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # do some pre-processing and return list of words for each review

                if i % 10000 == 0:
                    print("Processed {} elements after {} min".format(
                        i, int(((time.time() - t) / 60))))
                i += 1

                yield utils.simple_preprocess(line, max_len=500)


stcs, keys = DataBuilder.json_to_sentences_keys(
    r"Iris/files/order_datasets.json")

directory = r"C:\Users\Anthony Dard\OneDrive\VSC\Iris\DL\Saved\embedding_dataset"
#file_paths = find_paths(directory)

# Train on reddit
#data = XMLCorpus(os.path.join(directory, "final_SPF_2.xml"), "utt")

# Convert to lemmatized txt
# with open(os.path.join(directory, "reddit_lemmatized_sentences_2.txt"),
#           "a+",
#           encoding="utf-8") as f:
#     for sentence in data:
#         f.write(" ".join(sentence) + "\n")

data = MyCorpus(os.path.join(directory, "reddit_lemmatized_sentences.txt"))
model = Word2Vec(sentences=data,
                 size=150,
                 alpha=0.1,
                 min_alpha=0.00025,
                 min_count=8,
                 window=3,
                 sg=1,
                 workers=8)

model.build_vocab(data, update=True)
model.train(data, total_examples=model.corpus_count, epochs=4)

# Train on bibebooks
# t = time.time()
# for i, path in enumerate(file_paths):
#     print("Read corpus {} / {} at t = {} min".format(
#         i, len(file_paths), int((time.time() - t) / 60)))
#     corpus = MyCorpus(path)
#     model.build_vocab(corpus, update=True)
#     model.train(corpus, total_examples=model.corpus_count, epochs=6)

model.save(os.path.join(directory, "fr_reddit_lemma_150_skip.model"))

wv = model.wv
print(wv.most_similar(positive=[nlp('stop')[0].lemma_], topn=5))
