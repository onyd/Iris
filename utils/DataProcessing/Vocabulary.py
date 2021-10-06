from Iris.utils.DataProcessing.EntityRecognition import EntityRecognition
from tensorflow import keras


class Vocabulary:
    def __init__(self, nlp, settings=None, vocab={"<PAD>": 0, "<UNK>": 1}):
        self.vocab = vocab
        self.reverse_vocab = dict([(value, key)
                                   for key, value in self.vocab.items()])
        self.nlp = nlp
        self.settings = settings

    def __str__(self):
        return str(self.vocab)

    def __repr__(self):
        return dict.__repr__(self.vocab)

    def __len__(self):
        return len(self.vocab)

    def items(self):
        return self.vocab.items()

    def words(self):
        return self.vocab.keys()

    def get_word(self, index):
        return self.reverse_vocab.get(index, '<UNK>')

    def get_index(self, word):
        return self.vocab.get(word, 1)

    def add_word(self, word):
        if word.lower() not in self.vocab:
            self.vocab[word.lower()] = len(self.vocab)
            self.reverse_vocab = dict([(value, key)
                                       for key, value in self.vocab.items()])

    def build_vocabulary_from_sentences(self, sentences):
        for sentence in sentences:
            doc = self.get_doc(sentence)
            processed = self.process_doc(doc)
            for word in processed:
                self.add_word(word)

    def decode(self, encoded):
        return " ".join([self.reverse_vocab.get(i, 1) for i in encoded])

    def encode(self, *sentences):
        encoded = []
        for sentence in sentences:
            encoded.append(self.encode_doc(self.get_doc(sentence)))

        return keras.preprocessing.sequence.pad_sequences(
            encoded,
            value=self.get_index('<PAD>'),
            maxlen=self.settings.comparator['max_stc_len'],
            padding='post')

    def get_doc(self, sentence):
        doc = self.nlp(sentence)
        doc = EntityRecognition.merge_re_spacy(r"<.+?>", doc)

        return doc

    def encode_doc(self, doc):
        encoded = []

        processed = self.process_doc(doc)
        for word in processed:
            encoded.append(self.get_index(word))

        return encoded

    def process_doc(self, doc):
        processed = []
        for token in doc:
            if token.pos_ not in self.settings.comparator['exclude']:
                processed.append(token.lemma_)
        return processed

    def process_sentence(self, sentence):
        return self.process_doc(self.get_doc(sentence))