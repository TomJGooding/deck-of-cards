from __future__ import annotations

import random
from enum import Enum

from textual import events, on
from textual.app import App, ComposeResult
from textual.css.scalar import ScalarOffset
from textual.geometry import Offset
from textual.message import Message
from textual.reactive import var
from textual.widgets import Footer, Static


class CardSuit(Enum):
    DIAMONDS = 1
    CLUBS = 2
    HEARTS = 3
    SPADES = 4


SUIT_SYMBOLS = {
    CardSuit.DIAMONDS: chr(9830),
    CardSuit.CLUBS: chr(9827),
    CardSuit.HEARTS: chr(9829),
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
    dragged: var[bool] = var(False)

    class Grabbed(Message):
        def __init__(self, draggable: Draggable) -> None:
            super().__init__()
            self.draggable: Draggable = draggable

        @property
        def control(self) -> Draggable:
            return self.draggable

    def on_mouse_down(self, event: events.MouseDown) -> None:
        # dragged is set to False to differentate a mouse click from a
        # click-and-drag.
        self.dragged = False

        self.post_message(self.Grabbed(self))

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
            self.dragged = True

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

    def __init__(self, suit: CardSuit, rank: CardRank) -> None:
        super().__init__()
        self.suit = suit
        self.rank = rank

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
        if not self.dragged:
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


class DeckOfCardsApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "shuffle", "Shuffle"),
    ]

    CSS = """
    Screen {
        background: #008100;
        align: center middle;
    }
    """

    fresh_deck: var[bool] = var(True)

    def __init__(self) -> None:
        super().__init__()
        self.cards: list[Card] = self.init_deck()

    def init_deck(self) -> list[Card]:
        cards: list[Card] = []
        for suit in CardSuit:
            for rank in list(reversed(CardRank)):
                cards.append(Card(suit, rank))
        return cards

    def on_mount(self) -> None:
        layers = tuple([f"z-index-{i}" for i in range(1, 53)])
        self.screen.styles.layers = layers  # type: ignore [assignment]

    def compose(self) -> ComposeResult:
        z_index: int = 1
        for card in self.cards:
            card.styles.layer = f"z-index-{z_index}"
            yield card
            z_index = z_index + 1

        yield Footer()

    async def action_shuffle(self) -> None:
        if not self.fresh_deck:
            self._return_cards_to_deck()
            await self.animator.wait_until_complete()

        z_indexes = list(range(1, 53))
        random.shuffle(z_indexes)
        for card in self.cards:
            card.face_up = False
            card.styles.layer = f"z-index-{z_indexes.pop()}"

        layers = tuple([f"z-index-{i}" for i in range(1, 53)])
        self.screen.styles.layers = layers  # type: ignore [assignment]

        self.fresh_deck = True

    def _return_cards_to_deck(self) -> None:
        for card in self.cards:
            card.styles.animate(
                "offset",
                # workaround for https://github.com/Textualize/textual/issues/3028
                value=ScalarOffset.from_offset((0, 0)),  # type: ignore [arg-type]
                duration=0.2,
            )

    @on(Draggable.Grabbed)
    def on_card_grabbed(self, event: Draggable.Grabbed) -> None:
        self.fresh_deck = False

        current_layers = self.screen.layers
        new_layer = f"z-index-{len(current_layers) + 1}"
        self.screen.styles.layers = current_layers + (new_layer,)  # type: ignore [assignment]
        event.draggable.styles.layer = new_layer


def run() -> None:
    app = DeckOfCardsApp()
    app.run()
