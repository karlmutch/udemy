import random

from IPython.core.display import display, HTML
from IPython.display import clear_output

board = [
    "┌───┬───┬───┐",
    "│ 7 │ 8 │ 9 │",
    "├───┼───┼───┤",
    "│ 4 │ 5 │ 6 │",
    "├───┼───┼───┤",
    "│ 1 │ 2 │ 3 │",
    "└───┴───┴───┘"
]


class Card:
    def __init__(self, suit, rank, values, icon):
        self.suit = suit
        self.rank = rank
        self.values = list(values)
        self.icon = icon


class Deck():

    def __init__(self):
        self.cards = []
        generic_cards = [('ace', [1, 11])]
        for i in range(2, 11):
            generic_cards.append((f'{i}', [i]))
        for face in ['jack', 'queen', 'king']:
            generic_cards.append((face, [10]))

        cards_graphic = list('🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂽🂾🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂭🂮🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃍🃎🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃝🃞')

        for base, suit in enumerate(['hearts', 'spades', 'diamonds', 'clubs']):
            for i, card in enumerate(generic_cards):
                self.cards.append(Card(suit=suit, rank=card[0], values=card[1],
                                       icon=cards_graphic.pop(0)))

        random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        result = ''
        for card in self.cards:
            result += f'{card.icon}'
        return result

    def pop(self):
        return self.cards.pop()


class Hand():
    def __init__(self):
        self.cards = []

    def is_bust(self):
        total = 0
        for card in self.cards:
            total += min(card.values)
        return total > 21

    def is_blackjack(self):
        if self.is_bust():
            return False
        return 21 in self.totals()

    def append(self, card):
        self.cards.append(card)
        return not self.is_bust()

    def totals(self):
        totals = [0]
        for card in self.cards:
            if len(card.values) == 1:
                for i, total in enumerate(totals):
                    totals[i] += card.values[0]
                continue

            second_options = totals.copy()
            for i, total in enumerate(totals):
                totals[i] += card.values[0]
                second_options[i] += card.values[1]
            totals += second_options

        return list(filter(lambda x: x <= 21, set(totals)))

    def __str__(self):
        result = ''
        for card in self.cards:
            result += card.icon
        return result


class Player(Hand):
    def __init__(self):
        Hand.__init__(self)
        self.hidden = None

    def dealt_hidden(self, card):
        self.hidden = card

    def dealt(self, card):
        self.append(card)
        return not self.is_bust()

    def score(self):
        if len(self.totals()) == 0:
            return 0
        return max(self.totals())

    def __str__(self):
        result = Hand.__str__(self)
        if self.hidden is not None:
            result += '?'

        totals = self.totals()
        result += f' {totals}'
        return result


class Dealer(Player):
    def __init__(self):
        Player.__init__(self)

    def reveal(self):
        card = self.hidden
        self.dealt(card)
        self.hidden = None
        return card

    def is_standing(self):
        totals = self.totals()
        for total in totals:
            if total >= 17:
                return True
        return False


class Table():
    def __init__(self):
        self.dealer = Dealer()
        self.player = Player()

        self.deck = Deck()

        self.player.dealt(self.deck.pop())
        self.player.dealt(self.deck.pop())

        self.dealer.dealt(self.deck.pop())
        self.dealer.dealt_hidden(self.deck.pop())

        self.pot = 0

    def print(self):
        clear_output()
        print(f"Dealer {self.dealer}")
        print(f"Player {self.player}")

    def pot(self):
        return self.pot()

    def player_rounds(self, bank):
        while True:
            balance = bank.balance('player')
            bet = input(f'Please make your bet {balance} : ')
            try:
                if int(bet) <= 0:
                    continue
                bank.withdraw('player', int(bet))
                self.pot += int(bet)
                break
            except Exception as e:
                print(e)
                continue

        # Player chooses actions in a loop until they want to stop, hit 21, or are bust
        while True:
            self.print()
            if self.player.is_blackjack():
                print(f"player has blackjack")
                break
            while True:
                choice = input("'h'it or 's'tand : ")
                if choice in ['s', 'h']:
                    break

            if choice == 's':
                break

            card = self.deck.pop()
            if not self.player.dealt(card):
                print(f"player dealt {card.icon} and busted")
                break
            if self.player.is_blackjack():
                print(f"player dealt {card.icon} and has blackjack")
                break
            print(f"player dealt {card.icon}")

        return self.player.score()

    def dealer_rounds(self):
        # Dealer after players are done then exposes the hidden card
        # they continue pulling cards until they exceed 17, or bust
        if not self.player.is_bust():
            card = self.dealer.reveal()
            while True:
                self.print()
                if self.dealer.is_blackjack():
                    print(f"dealer dealt {card.icon} and has blackjack")
                    break
                if self.dealer.is_bust():
                    print(f'dealer is bust')
                    break
                if self.dealer.is_standing():
                    break
                card = self.deck.pop()
                self.dealer.dealt(card)

        return self.dealer.score()


class AccountExistsError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


class InSufficentFunds(Exception):
    pass


class Bank():

    def __init__(self):
        self.players = dict()

    def open(self, name, amount):
        if name in self.players:
            raise AccountExistsError()
        self.players[name] = amount

    def withdraw(self, name, amount):
        if name not in self.players:
            raise AccountNotFoundError()
        if self.players[name] < amount:
            raise InSufficentFunds()
        self.players[name] -= amount
        return self.players[name]

    def deposit(self, name, amount):
        if name not in self.players:
            raise AccountNotFoundError()
        if self.players[name] < amount:
            raise InSufficentFunds()
        self.players[name] -= amount
        return self.players[name]

    def balance(self, name):
        if name not in self.players:
            raise AccountNotFoundError()
        return self.players[name]


def run_hands(table, bank):

    player_score = table.player_rounds(bank)

    dealer_score = table.dealer_rounds()

    if not table.player.is_bust() and player_score > dealer_score:
        return 'player'

    return 'dealer'


def run_game(bank):

    if bank.balance('player') <= 0:
        raise InSufficentFunds()

    table = Table()
    winner = run_hands(table, bank)

    if winner == 'player':
        bank.deposit('player', table.pot)


def run():
    bank = Bank()

    bank.open('player', 100)

    while True:
        balance = bank.balance('player')
        print(f'player has {balance} chips')
        run_game(bank)


if __name__ == "__main__":
    try:
        run()
    except InSufficentFunds:
        print("Thank you for playing, bring more gold next time")
