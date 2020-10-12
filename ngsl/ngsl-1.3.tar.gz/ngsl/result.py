from operator import itemgetter


class Result:
    def __init__(self, ngsl_words, not_ngsl_words) -> None:
        self.ngsl_words = list(
            map(lambda el: el[0], sorted(ngsl_words, key=itemgetter(1))))
        self.not_ngsl_words = sorted(not_ngsl_words)
