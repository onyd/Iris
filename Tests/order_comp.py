from Iris.core.Listen.Matching.Matcher import OrderComparator
from Iris.Config.SettingsManager import SettingsManager

settings = SettingsManager()
comp = OrderComparator(settings)

import numpy as np
from Iris.DL.DataProcessing import DataGenerator


def check_similarity(sentence1, sentence2):
    sentence_pairs = np.array([[str(sentence1), str(sentence2)]])
    test_data = DataGenerator(
        sentence_pairs,
        labels=None,
        batch_size=1,
        max_len=settings.comparator['max_stc_len'],
        shuffle=False,
        include_targets=False,
    )

    proba = comp.model.predict(test_data)[0]
    idx = np.argmax(proba)
    proba = f"{proba[idx]: .2f}"
    return idx, proba


order = "Ajoute l'événement faire le dm à mon agenda"
tests = [
    "Bonjour !", "Où en est mon calendrier ?",
    "Ajoute l'événement <thing> le <date>"
]

for test in tests:
    print(check_similarity(order, test))
