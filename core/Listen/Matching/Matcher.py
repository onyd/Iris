from Iris.utils.Logging.ConsolePrinter import ConsolePrinter
from Iris.core.Listen.Matching.OrderComparator import OrderComparator
from Iris.core.Models.Reflexs.Reflexs import Reflexs
from Iris.core.Listen.Matching.ParamRecognizer import ParamRecognizer


class Matcher:
    def __init__(self, settings=None):
        self.settings = settings
        self.order_comparator = OrderComparator(settings)
        self.reflexs = Reflexs(settings)

    def match_by_signal(self, signal):
        ConsolePrinter.print_debug(
            f"Start searching a reflex corresponding to signal : {signal}")

        # Process order signal
        if signal['type'] == 'order':
            return self.match_by_order(order=signal['value'])

        else:
            return self.reflexs.find_reflex_by_signal(signal)

    def match_by_order(self, order):
        # Try to find some parameters which should simplify reflex matching for order comparator
        doc = self.settings.nlp(order)
        processed_order, params = ParamRecognizer.pre_recognize(order, doc)

        # We compare the signal to known ones and get the most similar reflex(for now just the name)
        reflex_name, trust_level = self.order_comparator(processed_order)[
            0]  # highest trust level
        reflex = self.reflexs.find_reflex_by_name(reflex_name)

        # params.update(
        #     ParamRecognizer.post_recognize(
        #         processed_order, doc, reflex, params,
        #         self.settings))  # TODO except placeholders

        ConsolePrinter.print_debug('Order matching summary :')
        ConsolePrinter.print_debug(f"->Reflex : {reflex_name}")
        ConsolePrinter.print_debug(f"->Trust level : {trust_level}")
        ConsolePrinter.print_debug(f"->Found params : {params}")
        ConsolePrinter.print_debug(
            f"->Corrected processed order : {processed_order}")

        return reflex, Matcher.build_buffer(params, reflex_name)

    @staticmethod
    def build_buffer(params, reflex_name):
        buffer = {}
        for placeholder, values in params.items():
            for i, value in enumerate(values):
                buffer[f'{placeholder}_{i}_{reflex_name}'] = value
