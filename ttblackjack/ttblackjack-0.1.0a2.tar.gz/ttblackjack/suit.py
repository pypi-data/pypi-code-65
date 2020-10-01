class Suit:
    def __init__(self, name, symbol) -> None:
        self.name = name
        self.symbol = symbol

    def __str__(self):
        return self.symbol
