# Made by Filip Stehlik
# Basic Lib for blackjack

#TO DO:
# Refactor, its ugly
# Add DAS control
# Add insurance controll for bot
# add more bot stuff

import random

class Shoe:
    def __init__(self, num_decks=1, penetration=0.75):
        self.num_decks = num_decks
        self.penetration = penetration
        self.cards = self.create_shoe(num_decks)
        self.reset_point = int(len(self.cards) * self.penetration)

    @staticmethod
    def create_shoe(num_decks):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        shoe = [{'suit': suit, 'rank': rank} for _ in range(num_decks) for suit in suits for rank in ranks]
        random.shuffle(shoe)
        return shoe

    def draw_card(self):
        if len(self.cards) <= self.reset_point:
            self.cards = self.create_shoe(self.num_decks)
            return 'RESET', None
        return None, self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        #print("Card object:", card)  # debug
        rank = card['rank']
        if rank == 'A':
            self.value += 11
            self.aces += 1
        elif rank in ['K', 'Q', 'J']:
            self.value += 10
        else:
            self.value += int(rank)
        self.adjust_for_ace()
    
    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def __str__(self):
        return ', '.join([f"{card['rank']} of {card['suit']}" for card in self.cards])

class BlackjackGame: 
    def __init__(self, num_decks=6, penetration=0.75, double_after_split=True):
        self.shoe = Shoe(num_decks)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.game_over = False
        self.split_hands = []
        self.insurance_bet = 0
        
    def reset(self):
        self.shoe = Shoe(self.shoe.num_decks)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.game_over = False

    def deal(self):
        _, card = self.shoe.draw_card()
        self.player_hand.add_card(card)
        _, card = self.shoe.draw_card()
        self.dealer_hand.add_card(card)
        _, card = self.shoe.draw_card()
        self.player_hand.add_card(card)
        _, card = self.shoe.draw_card()
        self.dealer_hand.add_card(card)


    def hit(self, hand):
        card_to_add = self._draw_card() 
        #print("Adding card:", card_to_add)
        hand.add_card(card_to_add)
        if hand.value > 21:
            self.game_over = True

    def stand(self):
        self.game_over = True

    def _draw_card(self):
        reset_signal, card = self.shoe.draw_card()
        if reset_signal == 'RESET':
            # You can add logic here to notify the player of the reset for card counting purposes.
            pass
        return card

    def can_split(self, hand):
        return len(hand.cards) == 2 and hand.cards[0]['rank'] == hand.cards[1]['rank']

    def play_hand(self, hand, bet):
        while hand.value < 21:
            print("Player's hand:", hand)
            action = input("Do you want to (h)it, (s)tand, (d)ouble, or (sp)lit? ").lower()
            if action == 'h':
                self.hit(hand)
            elif action == 's':
                return [hand], bet
            elif action == 'd':
                self.double_down(hand)
                bet *= 2
                return [hand], bet
            elif action == 'sp':
                if self.can_split(hand):
                    new_hand1 = Hand()
                    new_hand1.add_card(hand.cards.pop())
                    new_hand2 = Hand()
                    new_hand2.add_card(hand.cards.pop())
                    l = [self.play_hand(new_hand1, bet),self.play_hand(new_hand2, bet)]
                    return l, bet
                else:
                    print("unable")
            else:
                print("Invalid action. Try again.")

        print("Player's hand:", hand)
        return [hand], bet

    def can_double_down(self, hand):
        if hand in self.split_hands and not self.double_after_split:
            return False
        return len(hand.cards) == 2

    def double_down(self, hand):
        if self.can_double_down(hand):
            hand.add_card(self._draw_card())
            self.stand()

    def offer_insurance(self):
        return self.dealer_hand.cards[0]['rank'] == 'A'

    def take_insurance(self, bet_amount):
        self.insurance_bet = bet_amount

    def check_insurance(self):
        if self.insurance_bet > 0:
            dealer_has_blackjack = self.dealer_hand.value == 21 and len(self.dealer_hand.cards) == 2
            if dealer_has_blackjack:
                return self.insurance_bet * 2
            else:
                return -self.insurance_bet
        return 0

    def late_surrender(self, hand):
        self.game_over = True
        return -0.5

def play_game():
    print("Welcome to Blackjack!")
    game = BlackjackGame(penetration=0.25)
    player_balance = 1000

    while True:
        
        #bet
        print("Your current balance:", player_balance)
        bet = int(input("Enter your bet (integer): "))
        if bet > player_balance:
            print("You cannot bet more than your current balance. Try again.")
            continue
        if bet <= 0:
            print("Bet must be greater than 0. Try again.")
            continue
        
        #deal
        game.reset()
        game.deal()
        print("Player's hand:", game.player_hand)
        print("Dealer's upcard:", game.dealer_hand.cards[0])


        # Offer insurance if the dealer's upcard is an Ace
        if game.offer_insurance():
            insurance = input("Do you want to take insurance (y/n)? ").lower()
            if insurance == 'y':
                insurance_bet = bet / 2
                game.take_insurance(insurance_bet)
                print(f"You have taken insurance for {insurance_bet}")
        
        # Insurance logic
        insurance_result = game.check_insurance()
        player_balance += insurance_result
        if insurance_result > 0:
            print(f"Insurance paid! You won {insurance_result}")
        elif insurance_result < 0:
            print(f"You lost your insurance bet of {-insurance_result}")

       
        hands_to_evaluate, bet = game.play_hand(game.player_hand, bet)

        # Dealer's turn
        while game.dealer_hand.value < 17:
            game.hit(game.dealer_hand)

        for hand in hands_to_evaluate:
            print("Player's hand:", hand)
            print("Dealer's hand:", game.dealer_hand)
            # Check for player blackjack win
            if hand.value == 21 and len(hand.cards) == 2:
                if game.dealer_hand.value != 21 or len(game.dealer_hand.cards) != 2:
                    print("Blackjack! You win 3:2 on your bet!")
                    player_balance += bet * 1.5
            if game.dealer_hand.value == 21 and len(game.dealer_hand.cards) ==2:
                print("Dealer Blackjack! You lose!")
                player_balance -= bet
            elif hand.value > 21:
                print("Player busts! You lose.")
                player_balance -= bet
            elif game.dealer_hand.value > 21:
                print("Dealer busts! You win!")
                player_balance += bet
            elif hand.value > game.dealer_hand.value:
                print("You win!")
                player_balance += bet
            elif hand.value < game.dealer_hand.value:
                print("You lose.")
                player_balance -= bet
            else:
                print("It's a tie -> push.")

            if player_balance <= 0:
                print("You're out of money! Game over.")
                break

        play_again = input("Do you want to play again? (y/n): ").lower()
        if play_again != 'y':
            break
def bot_strategy(hand, strategy, dhand, s):
    
    a = False

    if dhand["rank"]  in ['K', 'Q', 'J']:
        dvalue = 10
    elif dhand["rank"] == 'A':
        dvalue = 11
    else:
        dvalue = int(dhand["rank"])

    if hand.aces !=0:  
        a = True

    basic_chart = [
            #[2,3,4,5,6,7,8,9,10,a]
            ['h','h','h','d','d','h','h','h','h','h'],#8
            ['h','d','d','d','d','h','h','h','h','h'],
            ['d','d','d','d','d','d','d','d','h','h'],
            ['d','d','d','d','d','d','d','d','d','d'],#11
            ['h','h','s','s','s','h','h','h','h','h'],
            ['s','s','s','s','s','h','h','h','h','h'],
            ['s','s','s','s','s','h','h','h','h','h'],
            ['s','s','s','s','s','h','h','h','h','h'],
            ['s','s','s','s','s','h','h','h','h','h']#16
    ]
    a_chart = [
            #[2,3,4,5,6,7,8,9,10,a]
            ['h','h','h','d','d','h','h','h','h','h'],#a-2 13
            ['h','h','d','d','d','h','h','h','h','h'],
            ['h','h','d','d','d','h','h','h','h','h'],
            ['d','h','d','d','d','h','h','h','h','h'],#a5
            ['h','d','d','d','d','h','h','h','h','h'],
            ['s','d','d','d','d','s','s','h','h','h'],#a7
            ['s','s','s','s','s','s','s','s','s','s'],
            ['s','s','s','s','s','s','s','s','s','s'],#a 9
            ['s','s','s','s','s','s','s','s','s','s'],#a 10
            ['h','h','s','s','h','h','h','h','h','h']#a a
    ]
    s_chart = [
            #[2,3,4,5,6,7,8,9,10,a]
            ['sp','sp','sp','sp','sp','sp','h','h','h','h'],#22
            ['sp','sp','sp','sp','sp','sp','h','h','h','h'],
            ['h','h','h','sp','sp','h','h','h','h','h'],
            ['d','d','d','d','d','d','d','d','h','h'],#55
            ['sp','sp','sp','sp','sp','h','h','h','h','h'],#66
            ['sp','sp','sp','sp','sp','sp','h','h','s','h'],#77
            ['sp','sp','sp','sp','sp','sp','sp','sp','sp','sp'],
            ['s','s','s','s','s','s','s','s','s','s'],#99
            ['s','s','s','s','s','s','s','s','s','s'],#1010
            ['sp','sp','sp','sp','sp','sp','sp','sp','sp','sp']#aa
    ]
    if strategy == "basic_split":
        if s:
            #print(s, hand)
            return s_chart[int((hand.value/2)) - 2][dvalue-2]
        elif a:
            #print(s,a,hand)
            return a_chart[int(hand.value)-13][dvalue-2]
        elif hand.value < 8:
            return 'h'
        elif hand.value > 16:
            return 's'
        else:
            return basic_chart[int(hand.value)-8][dvalue-2]
        
    elif strategy == "rng":
        return random.choice(["h", "s"])
    elif strategy == "onlyhit":
        return 'h'
    elif strategy == "onlystand":
        return 's'
    else:
        # Always Hit on 16 or less, and Stand on 17 or more
        return 'h' if hand.value <= 16 else 's'

class BotBlackjackGame(BlackjackGame):
    def play_hand(self, hand, bet, strategy, dhand):
        while hand.value < 21:
            action = bot_strategy(hand, strategy, dhand, self.can_split(hand))
            if action == 'h':
                self.hit(hand), bet
            elif action == 's':
                return [hand], bet
            elif action == 'd':
                self.double_down(hand)
                bet *= 2
                return [hand], bet
            elif action == 'sp':
                if self.can_split(hand):
                    new_hand1 = Hand()
                    new_hand1.add_card(hand.cards.pop())
                    new_hand2 = Hand()
                    new_hand2.add_card(hand.cards.pop())
                    [hand1], bet = self.play_hand(new_hand1, bet, "lol", dhand)
                    [hand2], bet = self.play_hand(new_hand2, bet, "lol", dhand)
                    return [hand1, hand2], bet

        return [hand], bet

def simulate_bot_play(rounds, initial_balance, betsize, strategy):
    player_balance = initial_balance
    game = BotBlackjackGame(penetration=0.25)
    balances = [player_balance]
    for _ in range(rounds):
        bet = int(betsize) 
        
        #deal
        game.reset()
        game.deal()
        #print("Player's hand:", game.player_hand)
        #print("Dealer's upcard:", game.dealer_hand.cards[0])

       
        hands_to_evaluate, bet = game.play_hand(game.player_hand, bet, strategy, game.dealer_hand.cards[0])

        # Dealer's turn
        while game.dealer_hand.value < 17:
            game.hit(game.dealer_hand)

        for hand in hands_to_evaluate:
            #print(hand)
            if hand.value == 21 and len(hand.cards) == 2:
                if game.dealer_hand.value != 21 or len(game.dealer_hand.cards) != 2:
                    player_balance += bet * 1.5
            elif game.dealer_hand.value == 21 and len(game.dealer_hand.cards) ==2:
                #print("Dealer Blackjack! You lose!")
                player_balance -= bet
            elif hand.value > 21:
                player_balance -= bet
            elif game.dealer_hand.value > 21:
                player_balance += bet
            elif hand.value > game.dealer_hand.value:
                player_balance += bet
            elif hand.value < game.dealer_hand.value:
                player_balance -= bet
            else:
                pass
        balances.append(player_balance)
    return balances

def botplay(rounds = 100, initial_balance = 1000, betsize = 10, strategy = "basic", include_insurance=False):

    final_balance = simulate_bot_play(rounds, initial_balance, betsize, strategy)
    return final_balance
    #print(f"After {rounds} rounds, the bot's balance is {final_balance}")

if __name__ == "__main__":
    #play_game()
    print(botplay(strategy = ""))
