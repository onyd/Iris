from dateparser.search import search_dates
import re

from Iris.utils.DataProcessing.EntityRecognition import EntityRecognition


class ParamRecognizer:
    placeholders = {
        'ORG': '<org>',
        'LOC': '<loc>',
        'PER': '<per>',
        'DEVICE': '<device>',
        'APP': '<app>'
    }

    @staticmethod
    def process_order(order, params):
        for placeholder, value in params.items():
            re.sub(value, placeholder, order)

        return order

    @staticmethod
    def pre_recognize(order, doc):
        params = {
            '<org>': [],
            '<loc>': [],
            '<per>': [],
            '<device>': [],
            '<app>': [],
            '<time>': []
        }

        # Dates
        params['<time>'] = search_dates(
            order,
            settings={
                'PREFER_DATES_FROM': 'future',
                'SKIP_TOKENS': ['lu', 'ma', 'me', 'je', 've', 'sa', 'di']
            })

        # Spacy NER
        for ent in doc.ents:
            params[ParamRecognizer.placeholders[ent.label_]].append(ent.text)

        return params, ParamRecognizer.process_order(order, params)

    # @staticmethod
    # def post_recognize(order, doc, reflex, params, settings):
    #     expected_placeholder = [param.placeholder for param in params]

    #     texts = []
    #     # Search for corresponding sequence
    #     if except_words and expected_placeholder and settings.nlp:
    #         sequence = EntityRecognition.find_enclosed_sequence(
    #             order, except_words, expected_placeholder, settings, doc)
    #         if sequence != "":
    #             texts.append(sequence)
    #     else:
    #         texts.append(order)

    # @staticmethod
    # def get_reflex_signals_words(reflex, doc):
    #     except_words = []
    #     for signal in reflex.signals:
    #         if signal.type == 'order':
    #             order = signal.values['order']
    #             order = re.sub("<.+?>", "", order)

    #             for token in doc:
    #                 # We don't count those class of words which can be easily found in param
    #                 if token.lemma_ not in except_words and token.pos_ not in [
    #                         'ADP', 'AUX', 'CONJ', 'DET', 'NUM', 'PART', 'PRON',
    #                         'SCONJ', 'PUNCT', 'SYM', 'X'
    #                 ]:
    #                     except_words.append(token.lemma_)
    #     return list(
    #         filter(lambda x: x not in [' ', '', ',', '-'], except_words))

    # @staticmethod
    # def get_expected_placeholders(reflex):
    #     posible_placeholders = []
    #     for signal in reflex.signals:
    #         if signal.type == 'order':
    #             p = re.compile(r"<.+?>")
    #             for placeholder in p.findall(signal.values['order']):
    #                 if placeholder not in posible_placeholders:
    #                     posible_placeholders.append(placeholder)

    #     return posible_placeholders