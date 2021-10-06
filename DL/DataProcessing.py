from itertools import combinations
import pandas as pd
import numpy as np
import tensorflow as tf
from transformers import AutoTokenizer

from Iris.utils.FileProcessing.FileManager import FileManager


class DataGenerator(tf.keras.utils.Sequence):
    """Generates batches of data.

    Args:
        sentence_pairs: Array of premise and hypothesis input sentences.
        labels: Array of labels.
        batch_size: Integer batch size.
        shuffle: boolean, whether to shuffle the data.
        include_targets: boolean, whether to incude the labels.

    Returns:
        Tuples `([input_ids, attention_mask, `token_type_ids], labels)`
        (or just `[input_ids, attention_mask, `token_type_ids]`
         if `include_targets=False`)
    """
    def __init__(
        self,
        sentence_pairs,
        labels=None,
        batch_size=1,
        max_len=16,
        shuffle=True,
    ):
        self.max_len = max_len
        self.labels = labels
        self.shuffle = shuffle
        self.batch_size = batch_size

        self.tokenizer = AutoTokenizer.from_pretrained(
            "jplu/tf-camembert-base")
        self.indexes = np.arange(len(sentence_pairs))
        self.encoded = self.encode_pairs(sentence_pairs)
        self.on_epoch_end()

    def encode_pairs(self, sentence_pairs):
        out = []
        for i in range(len(sentence_pairs) // self.batch_size):
            encoded = self.tokenizer.batch_encode_plus(
                sentence_pairs.tolist(),
                add_special_tokens=True,
                max_length=self.max_len,
                truncation=True,
                return_attention_mask=True,
                return_token_type_ids=True,
                padding=True,
                return_tensors="tf",
            )
            input_ids = np.array(encoded["input_ids"], dtype="int32")
            attention_masks = np.array(encoded["attention_mask"],
                                       dtype="int32")
            token_type_ids = np.array(encoded["token_type_ids"], dtype="int32")

            if self.labels is not None:
                labels = np.array(self.labels[i * self.batch_size:(i + 1) *
                                              self.batch_size],
                                  dtype="int32")
                out.append(([input_ids, attention_masks,
                             token_type_ids], labels))
            else:
                out.append([input_ids, attention_masks, token_type_ids])
        return out

    def __len__(self):
        # Denotes the number of batches per epoch.
        return len(self.indexes) // self.batch_size

    def __getitem__(self, idx):
        return self.encoded[self.indexes(idx)]

    def on_epoch_end(self):
        # Shuffle indexes after each epoch if shuffle is set to True.
        if self.shuffle:
            np.random.RandomState(42).shuffle(self.indexes)


class DataBuilder:
    @staticmethod
    def flatten_dict(data):
        flattened = []
        for name, orders in data.items():
            for order in orders:
                flattened.append((name, order))
        return flattened

    @staticmethod
    def to_csv(data, csv_path):
        couples = list(combinations(DataBuilder.flatten_dict(data), 2))

        left_orders = []
        right_orders = []
        labels = []
        for left, right in couples:
            left_orders.append(left[1])
            right_orders.append(right[1])
            labels.append(int(left[0] == right[0]))

        df = pd.DataFrame({
            'left': pd.Series(left_orders),
            'right': pd.Series(right_orders),
            'labels': pd.Series(labels)
        })

        df.to_csv(csv_path)


if __name__ == "__main__":
    path = "Iris/resources/files/order_datasets.json"
    DataBuilder.to_csv(FileManager.load_json(path), path[:-4] + "csv")
