from discord.ext import commands
import chess
import random

#not completed, just a showcase, therefore code is shit
class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = None
        self.current_player = None
    #start game

    @commands.command()
    async def chess(self, message, arg):
        """Plays chess, first time to ini, then make moves"""
        if self.board is None:
            self.board = chess.Board()
            self.current_player = message.author
            moves =list(self.board.legal_moves)
            move = random.choice(moves)
            move = str(move)
            self.board.push_san(move)
            await message.send("Hra začla, posílej tahy ve formátu z políčka do políčka - a7a6")
            await message.send(move)
            await message.send(self.board)
            return          
        if message.author == self.current_player:
            arg = str(arg)
            print(arg, list(self.board.legal_moves) )
            if chess.Move.from_uci(arg) in list(self.board.legal_moves):
                self.board.push_san(arg)
                if self.board.is_checkmate():
                    self.board =None
                    self.current_player=None
                    await message.send("gameover")
                    return
                moves =list(self.board.legal_moves)
                move = random.choice(moves)
                move = str(move)
                self.board.push_san(move)
                await message.send(move)
                await message.send(self.board)
                if self.board.is_checkmate():
                    await message.send("gameover")
            else:
                await message.send("invadid move bro")
        else:
            await message.send(f"you are not playing rn, this user is playing:{self.current_player}")


async def setup(bot):
    await bot.add_cog(ChessCog(bot))