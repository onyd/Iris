import re

from Iris.utils.Structures.Lifo import Lifo


class EntityRecognition:
    @staticmethod
    def find_enclosed_sequence(text,
                               except_words,
                               expected_params,
                               settings,
                               doc=None):
        reflex_sequences = Lifo()
        params_sequences = Lifo()

        # Tokenized the order
        if not doc:
            doc = settings.nlp(text)
            doc = EntityRecognition.merge_re_spacy(r"<.+?>", doc)

        buffer = ""
        stops_buffer = ""
        is_params_sequence = False
        # Build the Lifo
        for token in doc:
            # A stop words and known params break sequence
            if token.pos_ in settings.comparator['exclude']:
                stops_buffer += " " + token.lower_

            elif token.lower_ in expected_params:

                buffer, is_params_sequence = EntityRecognition.broke_sequence(
                    is_params_sequence, buffer, token, reflex_sequences,
                    params_sequences)
                stops_buffer = ""

            # An except word break params seaquence but continue reflex sequence
            elif token.lower_ in except_words:
                if is_params_sequence:
                    buffer, is_params_sequence = EntityRecognition.broke_sequence(
                        is_params_sequence, buffer, token, reflex_sequences,
                        params_sequences)
                    buffer = stops_buffer + buffer
                    stops_buffer = ""
                else:
                    buffer += stops_buffer + " " + token.lower_
                    stops_buffer = ""

            # Otherwise the params sequence continue or the reflex sequence is broken
            else:
                if is_params_sequence:
                    buffer += stops_buffer + " " + token.lower_
                    stops_buffer = ""
                else:
                    buffer, is_params_sequence = EntityRecognition.broke_sequence(
                        is_params_sequence, buffer, token, reflex_sequences,
                        params_sequences)
                    buffer = stops_buffer + buffer
                    stops_buffer = ""

        print("params_sequences", params_sequences)
        print("reflex_sequences", reflex_sequences)
        sequence = ""
        while len(params_sequences) > 0:
            sequence = params_sequences.pop() + " " + sequence
            # We suppose that parameter is unique and "one shot given" so we keep non matched words between and concatenate the sequences
            if len(reflex_sequences) > 0 and len(params_sequences) > 0:
                sequence = reflex_sequences.pop() + " " + sequence

        return sequence

    @staticmethod
    def broke_sequence(is_params_sequence, buffer, current_token,
                       reflex_sequences, params_sequences):
        if is_params_sequence:
            params_sequences.push(buffer)
        else:
            reflex_sequences.push(buffer)

        buffer = current_token.lower_
        is_params_sequence = not is_params_sequence
        return buffer, is_params_sequence

    @staticmethod
    def merge_re_spacy(expr, doc):
        for match in re.finditer(expr, doc.text):
            start, end = match.span()
            span = doc.char_span(start, end)
            if span is not None:
                with doc.retokenize() as retokenizer:
                    retokenizer.merge(span)

        return doc
