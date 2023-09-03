from discord.ext import commands
import sys
sys.path.append("..")
from blackjack import *

class blackjackcog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game = None
        self.player_balance = 1000

    @commands.command()
    async def blackjack(self, ctx, arg=None):
        if self.game is None:
            self.game = DiscordBlackjackGame(penetration=0.25, bot=self.bot)
            await ctx.send("Welcome to Blackjack!")
            await ctx.send(f"Your current balance: {self.player_balance}")
            return
        
        if arg == 'reset':
            self.game = None
            self.player_balance = 1000
            await ctx.send("Game has been reset.")
            return

        bet = int(arg)
        if bet > self.player_balance:
            await ctx.send("You cannot bet more than your current balance. Try again.")
            return
        if bet <= 0:
            await ctx.send("Bet must be greater than 0. Try again.")
            return

        self.game.reset()
        self.game.deal()
        await ctx.send(f"Player's hand: {self.game.player_hand}")
        await ctx.send(f"Dealer's upcard: {self.game.dealer_hand.cards[0]}")
        
        if self.game.offer_insurance():
            # Assume insurance is taken for this example. Add your own mechanism to ask user.
            insurance_bet = bet / 2
            self.game.take_insurance(insurance_bet)
            await ctx.send(f"You have taken insurance for {insurance_bet}")

        insurance_result = self.game.check_insurance()
        self.player_balance += insurance_result
        if insurance_result > 0:
            await ctx.send(f"Insurance paid! You won {insurance_result}")
        elif insurance_result < 0:
            await ctx.send(f"You lost your insurance bet of {-insurance_result}")

        hands_to_evaluate, bet = await self.game.play_hand(ctx, self.game.player_hand, bet)
        
        while self.game.dealer_hand.value < 17:
            self.game.hit(self.game.dealer_hand)
        
        for hand in hands_to_evaluate:
            await ctx.send(f"Player's hand: {hand}")
            await ctx.send(f"Dealer's hand: {self.game.dealer_hand}")

            if hand.value == 21 and len(hand.cards) == 2:
                if self.game.dealer_hand.value != 21 or len(self.game.dealer_hand.cards) != 2:
                    await ctx.send("Blackjack! You win 3:2 on your bet!")
                    self.player_balance += bet * 1.5
            if self.game.dealer_hand.value == 21 and len(self.game.dealer_hand.cards) == 2:
                await ctx.send("Dealer Blackjack! You lose!")
                self.player_balance -= bet
            elif hand.value > 21:
                await ctx.send("Player busts! You lose.")
                self.player_balance -= bet
            elif self.game.dealer_hand.value > 21:
                await ctx.send("Dealer busts! You win!")
                self.player_balance += bet
            elif hand.value > self.game.dealer_hand.value:
                await ctx.send("You win!")
                self.player_balance += bet
            elif hand.value < self.game.dealer_hand.value:
                await ctx.send("You lose.")
                self.player_balance -= bet
            else:
                await ctx.send("It's a tie -> push.")
            
            if self.player_balance <= 0:
                await ctx.send("You're out of money! Game over.")
                self.game = None
                return

        await ctx.send(f"Do you want to play again? If yes, place a new bet. Current balance: {self.player_balance}")

async def setup(bot):
    await bot.add_cog(blackjackcog(bot))


class DiscordBlackjackGame(BlackjackGame):
    def __init__(self, penetration, bot):
        super().__init__(penetration=penetration)
        self.bot = bot
    async def play_hand(self, ctx, hand, bet):
        hands_to_evaluate = []
        while hand.value < 21:
            await ctx.send(f"Player's hand: {hand}")
            await ctx.send("Do you want to (h)it, (s)tand, (d)ouble, or (sp)lit?")
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for('message', check=check)
            action = msg.content.lower()

            if action == 'h':
                self.hit(hand)
            elif action == 's':
                hands_to_evaluate.append(hand)
                return hands_to_evaluate, bet
            elif action == 'd':
                self.double_down(hand)
                bet *= 2
                hands_to_evaluate.append(hand)
                return hands_to_evaluate, bet
            elif action == 'sp':
                if self.can_split(hand):
                    new_hand1 = Hand()
                    new_hand2 = Hand()
                    new_hand1.add_card(hand.cards.pop())
                    new_hand2.add_card(hand.cards.pop())
                    
                    results1, _ = await self.play_hand(ctx, new_hand1, bet)
                    results2, _ = await self.play_hand(ctx, new_hand2, bet)
                    hands_to_evaluate.extend(results1)
                    hands_to_evaluate.extend(results2)
                    
                    return hands_to_evaluate, bet
                else:
                    await ctx.send("You can't split this hand.")
            else:
                await ctx.send("Invalid action. Try again.")

        await ctx.send(f"Player's hand: {hand}")
        hands_to_evaluate.append(hand)
        return hands_to_evaluate, bet
