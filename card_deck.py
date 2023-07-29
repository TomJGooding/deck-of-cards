from enum import Enum

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static


class CardSuit(Enum):
    CLUBS = 1
    HEARTS = 2
    DIAMONDS = 3
    SPADES = 4


SUIT_SYMBOLS = {
    CardSuit.CLUBS: chr(9827),
    CardSuit.HEARTS: chr(9829),
    CardSuit.DIAMONDS: chr(9830),
    CardSuit.SPADES: chr(9824),
}


class CardRank(Enum):
    ACE = 1
    DEUCE = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


RANK_SYMBOLS = {
    CardRank.ACE: "A",
    CardRank.JACK: "J",
    CardRank.QUEEN: "Q",
    CardRank.KING: "K",
}


class Card(Static):
    DEFAULT_CSS = """
    Card {
        background: white;
        width: 10;
        height: 8;
        content-align: center middle;
    }
    """

    def __init__(self, rank: CardRank, suit: CardSuit) -> None:
        super().__init__()
        self.rank = rank
        self.suit = suit

    def render(self) -> RenderableType:
        card_face = "\n".join(
            [
                f"{self.rank_symbol : <4}{self.suit_symbol : >4}",
                "\n",
                "\n",
                f"{self.suit_symbol : <4}{self.rank_symbol : >4}",
            ]
        )
        return card_face

    def on_mount(self) -> None:
        if self.suit in (CardSuit.HEARTS, CardSuit.DIAMONDS):
            self.styles.color = "red"
        else:
            self.styles.color = "black"

    @property
    def suit_symbol(self) -> str:
        return SUIT_SYMBOLS[self.suit]

    @property
    def rank_symbol(self) -> str:
        rank_symbol = RANK_SYMBOLS.get(self.rank)
        if rank_symbol is not None:
            return rank_symbol
        else:
            return str(self.rank.value)


class CardDeckApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    CSS = """
    Screen {
        background: #008100;
        align: center middle
    }
    """

    def compose(self) -> ComposeResult:
        yield Card(CardRank.TEN, CardSuit.DIAMONDS)
        yield Footer()


if __name__ == "__main__":
    app = CardDeckApp()
    app.run()
