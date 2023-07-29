from enum import Enum

from rich.console import RenderableType
from textual import events
from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.reactive import var
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


class Draggable(Static):
    mouse_at_drag_start: var[Offset | None] = var(None)
    offset_at_drag_start: var[Offset | None] = var(None)

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.mouse_at_drag_start = event.screen_offset
        self.offset_at_drag_start = Offset(
            round(self.styles.offset.x.value),
            round(self.styles.offset.y.value),
        )
        self.capture_mouse()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if (
            self.mouse_at_drag_start is not None
            and self.offset_at_drag_start is not None
        ):
            self.styles.offset = (
                self.offset_at_drag_start
                + event.screen_offset
                - self.mouse_at_drag_start
            )

    def on_mouse_up(self, event: events.MouseUp) -> None:
        self.mouse_at_drag_start = None
        self.offset_at_drag_start = None
        self.release_mouse()
        event.stop()


class Card(Draggable):
    DEFAULT_CSS = """
    Card {
        background: white;
        width: 8;
        height: 6;
    }
    """

    face_up: var[bool] = var(False)

    def __init__(self, rank: CardRank, suit: CardSuit) -> None:
        super().__init__()
        self.rank = rank
        self.suit = suit

    def watch_face_up(self, face_up: bool) -> None:
        self.update(self.face) if face_up else self.update(self.back)
        if not face_up:
            self.styles.color = "blue"
            return

        if self.suit in (CardSuit.HEARTS, CardSuit.DIAMONDS):
            self.styles.color = "red"
        else:
            self.styles.color = "black"

    def on_click(self) -> None:
        self.face_up = not self.face_up

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

    @property
    def face(self) -> str:
        card_face = "\n".join(
            [
                f"{self.rank_symbol : <4}{self.suit_symbol : >4}",
                "\n",
                "\n",
                f"{self.suit_symbol : <4}{self.rank_symbol : >4}",
            ]
        )
        return card_face

    @property
    def back(self) -> str:
        card_back = "\n".join([(chr(9618) * 8) for _ in range(6)])
        return card_back


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
