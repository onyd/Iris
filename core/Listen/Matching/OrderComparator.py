import os
import numpy as np
import tensorflow as tf
import pandas as pd
from transformers import TFAutoModel

from Iris.utils.Logging.ConsolePrinter import ConsolePrinter
from Iris.DL.Models.Siamese import Siamese
from Iris.DL.DataProcessing import DataBuilder, DataGenerator
from Iris.utils.DataProcessing.Vocabulary import Vocabulary
from Iris.utils.FileProcessing.FileManager import FileManager


class OrderComparator:
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings
        # try to load existing model else we create a new model
        #if not self.load():
        self.reboot()

    def setup_model(self):
        """If the model is not found in settings path
        then we load the word2vec model and train with available data"""

        strategy = tf.distribute.MirroredStrategy()

        with strategy.scope():
            # Encoded token ids from BERT tokenizer.
            input_ids = tf.keras.layers.Input(
                shape=(self.settings.comparator['max_stc_len'], ),
                dtype=tf.int32,
                name="input_ids")
            # Attention masks indicates to the model which tokens should be attended to.
            attention_masks = tf.keras.layers.Input(
                shape=(self.settings.comparator['max_stc_len'], ),
                dtype=tf.int32,
                name="attention_masks")
            # Token type ids are binary masks identifying different sequences in the model.
            token_type_ids = tf.keras.layers.Input(
                shape=(self.settings.comparator['max_stc_len'], ),
                dtype=tf.int32,
                name="token_type_ids")
            # Loading pretrained BERT model.
            bert_model = TFAutoModel.from_pretrained("jplu/tf-camembert-base")
            # Freeze the BERT model to reuse the pretrained features without modifying them.
            bert_model.trainable = False

            sequence_output, _ = bert_model(input_ids,
                                            attention_mask=attention_masks,
                                            token_type_ids=token_type_ids)
            # Add trainable layers on top of frozen layers to adapt the pretrained features on the new data.
            bi_lstm = tf.keras.layers.Bidirectional(
                tf.keras.layers.LSTM(16,
                                     return_sequences=True))(sequence_output)
            # Applying hybrid pooling approach to bi_lstm sequence output.
            #avg_pool = tf.keras.layers.GlobalAveragePooling1D()(bi_lstm)
            max_pool = tf.keras.layers.GlobalMaxPooling1D()(bi_lstm)
            #concat = tf.keras.layers.concatenate([avg_pool, max_pool])
            dropout = tf.keras.layers.Dropout(0.3)(max_pool)
            output = tf.keras.layers.Dense(2, activation="softmax")(dropout)

            self.model = tf.keras.models.Model(
                inputs=[input_ids, attention_masks, token_type_ids],
                outputs=output)

    def build_model(self):

        optimizer = tf.keras.optimizers.Adam(
            learning_rate=self.settings.comparator['learning_rate'],
            epsilon=1e-7)

        self.model.compile(optimizer=optimizer,
                           loss="categorical_crossentropy",
                           metrics=['accuracy'])

    def reboot(self):
        self.setup_model()
        self.build_model()
        self.train()

    def __call__(self, sentence, n_similars=1):
        """The sentence is compared to the ones that exists in order signals
        and try to find the most similar one(s)"""
        doc = self.voc.get_doc(sentence)
        #self.learn_unk_words(doc)

        stc1 = self.voc.encode_doc(doc)
        stc1 = DataBuilder.sentences_pre_processing(
            self.voc, [stc1], self.settings.comparator['max_stc_len'])[0]
        # Build couples with given sentence
        cpl = {'left': [], 'right': []}
        for stc2 in self.processed:
            cpl['left'].append(stc1)
            cpl['right'].append(stc2)

        left = np.array(cpl['left'])
        right = np.array(cpl['right'])
        predictions = self.model.predict([left, right])

        # Get n_similars distinct most similars to stc1
        most_similars = []
        i = 0
        n = 0
        while i < predictions.shape[0] and n < n_similars:
            m = np.argmax(predictions)
            if self.keys[m] not in [key[0] for key in most_similars]:
                most_similars.append((self.keys[m], predictions[m, 0]))
                n += 1
            predictions[m] = 0.  # so it will not be counted anymore
            i += 1
        return most_similars

    def train(self):
        train_df = pd.read_csv(self.settings.paths['order_data_path'] + ".csv",
                               index_col=0)

        # Show some info on dataset
        print("Train Target Distribution")
        print(train_df.labels.value_counts())

        train_df = train_df.sample(frac=1.0,
                                   random_state=42).reset_index(drop=True)

        # Data generation
        y_train = tf.keras.utils.to_categorical(train_df.labels, num_classes=2)
        train_data = DataGenerator(
            train_df[["left", "right"]].values.astype("str"),
            labels=y_train,
            batch_size=self.settings.comparator['batch_size'],
            max_len=self.settings.comparator['max_stc_len'],
            shuffle=True)
        history = self.model.fit(train_data,
                                 epochs=self.settings.comparator['epochs'],
                                 shuffle=False)

        return history

    def load(self):
        ConsolePrinter.print_debug(
            "Try to load existing serialized comparator")
        try:
            # Load vocabulary
            path = os.path.join(self.settings.paths['comp_model'], "voc.json")
            self.voc = Vocabulary(self.settings.nlp, self.settings,
                                  FileManager.load_json(path))
            ConsolePrinter.print_debug(
                "Succesfully loaded existing vocabulary")
            # Load processed with keys
            path = os.path.join(self.settings.paths['comp_model'],
                                "processed.json")
            self.processed = np.array(FileManager.load_json(path))
            ConsolePrinter.print_debug(
                "Succesfully loaded existing processed sentences")
            path = os.path.join(self.settings.paths['comp_model'], "keys.json")
            self.keys = FileManager.load_json(path)
            ConsolePrinter.print_debug(
                "Succesfully loaded existing associated keys")

            # Load model
            path = os.path.join(self.settings.paths['comp_model'],
                                "comparator_shared")
            shared = tf.keras.models.load_model(path)
            self.build_model(shared)
            ConsolePrinter.print_debug(
                "Succesfully loaded existing shared model")
            return True
        except:
            ConsolePrinter.print_warning(
                "Error in loading existing comparator, a new one will be created"
            )
            return False

    def save(self):
        try:
            # Save vocabulary
            path = os.path.join(self.settings.paths['comp_model'], "voc.json")
            FileManager.save_json(path, self.voc.vocab)

            # Load processed with keys
            path = os.path.join(self.settings.paths['comp_model'],
                                "processed.json")
            FileManager.save_json(path, self.processed.tolist())
            path = os.path.join(self.settings.paths['comp_model'], "keys.json")
            FileManager.save_json(path, self.keys)

            # Save the model according to settings path
            path = os.path.join(self.settings.paths['comp_model'],
                                "comparator_shared")
            self.model.shared.save(path)
            ConsolePrinter.print_debug("Succesfully saved shared model")
        except IOError:
            ConsolePrinter.print_error(
                "The comparator did not success saving all parameters, consider to retry saving"
            )
