import tkinter as tk
from tkinter import simpledialog, filedialog
from asyncio import *
import threading # tkinter neumi asynchronni vlakna, proto je nutne pouzit threading
from queue import Queue # pro predavani dat mezi vlakny
from queue import Empty as ERROR_QUEUE_EMPTY

import discord                                        # Discord API
# -- import requests                                       # knihovna pro HTTP requesty
from bs4 import BeautifulSoup                         # knihovna pro parsovani HTML
from discord.ext.commands import Bot, has_permissions # knihovna pro Discord boty

# konstanty pro snapovani bloku
TRESHOLD = 5
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000

# Discord bot starts here

class BotCore:
    _instance = None

    def __new__(cls): #, in_token):
        if cls._instance is None:
            cls._instance = super(BotCore, cls).__new__(cls)
        return cls._instance

    def __init__(self): 
        self.token = global_receive_from_queue()

        intents = discord.Intents.all()                                         # Intents jsou "zapouzrena" nastaveni discord opravneni pro bota
        intents.typing = True                                                   # Urcuje, jestli bot muze psat zpravy
        intents.presences = True                                                # Urcuje, jestli muze bot videt, kdyz se nekdo pripoji nebo odpoji

        self.bot = Bot(command_prefix='/', intents=intents)

        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} has connected to Discord!')

    def run(self, token):
        self.bot.run(token) #TODO: ERR: cannot be run in async thread

    async def setup_hook(self):
        global rectangles
        for item in rectangles:
            try:
                self.bot.unload_extension(item.associated_file)
            except:
                pass # intentional pass
            if item.is_active:
                await self.bot.load_extension(item.associated_file)

def discord_bot_loop():
    global predavaci_fronta
    token = predavaci_fronta.get()
    bot_core = BotCore()
    bot_core.run(token)

# TKinter starts here

class SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill, input_root):
        self.root = input_root
        self.canvas = canvas
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, tags="rectangle")
        self.connected_rectangles = []
        self.delete_button = tk.Button(canvas, text="Delete", command=self.root.delete_rectangle)
        self.associated_file = None
        self.is_active = False

class Tk_extended(tk.Tk):
    def __init__(self):
        super().__init__()
        self.rectangles = []
        self.delete_buttons = {}
        self.selected_rectangle = None
        self.token = None
        self.canvas = None

    def delete_rectangle(self):
        #TODO: odstranit pripojeny soubor ze slozky pro cogy
        for rect in self.connected_rectangles:
            rect.connected_rectangles.remove(self)
        self.canvas.delete(self.rect)
        self.delete_button.destroy()

    def on_click(self, event):
        global prev_x, prev_y, selected_rectangle
        prev_x, prev_y = event.x, event.y
        selected_rectangle = self.canvas.find_closest(event.x, event.y)[0]

    def on_drag(self, event):
        #TODO: nefunguje, nwm proc
        global prev_x, prev_y
        x, y = event.x - prev_x, event.y - prev_y
        if self.selected_rectangle:
            snapped_rect = self.snap_together(self.selected_rectangle, x, y)
            if snapped_rect:
                selected_rectangle.is_active = True
                self.align_rectangles(selected_rectangle, snapped_rect, x, y)
            else:
                selected_rectangle.is_active = False
                self.canvas.move(selected_rectangle, x, y)
                self.move_delete_button(selected_rectangle, x, y)
        prev_x, prev_y = event.x, event.y

    def snap_together(self, rect, x, y):
        threshold = TRESHOLD  # Adjust this value to control the snap sensitivity
        bbox = self.canvas.bbox(rect)

        for other_rect in rectangles:
            if other_rect.rect != rect:
                other_bbox = self.canvas.bbox(other_rect.rect)
                if other_bbox:
                    # Check distance between sides
                    x_distance_left = abs(bbox[0] - other_bbox[2])
                    x_distance_right = abs(bbox[2] - other_bbox[0])
                    y_distance_top = abs(bbox[1] - other_bbox[3])
                    y_distance_bottom = abs(bbox[3] - other_bbox[1])

                    if x_distance_left < threshold and 0 < y_distance_bottom < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]):
                        return other_rect.rect
                    elif x_distance_right < threshold and 0 < y_distance_top < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]):
                        return other_rect.rect
                    elif y_distance_top < threshold and 0 < x_distance_right < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]):
                        return other_rect.rect
                    elif y_distance_bottom < threshold and 0 < x_distance_left < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]):
                        return other_rect.rect

        return None

    def align_rectangles(self, rect1, rect2, x, y):
        bbox1 = self.canvas.bbox(rect1)
        bbox2 = self.canvas.bbox(rect2)

        x_distance_left = abs(bbox1[0] - bbox2[2])
        x_distance_right = abs(bbox1[2] - bbox2[0])
        y_distance_top = abs(bbox1[1] - bbox2[3])
        y_distance_bottom = abs(bbox1[3] - bbox2[1])

        if x_distance_left < x_distance_right and x_distance_left < y_distance_top and x_distance_left < y_distance_bottom:
            x_offset = bbox2[2] - bbox1[0]
            y_offset = 0
        elif x_distance_right < y_distance_top and x_distance_right < y_distance_bottom:
            x_offset = bbox2[0] - bbox1[2]
            y_offset = 0
        elif y_distance_top < y_distance_bottom:
            x_offset = 0
            y_offset = bbox2[3] - bbox1[1]
        else:
            x_offset = 0
            y_offset = bbox2[1] - bbox1[3]

        self.canvas.move(rect1, x + x_offset, y + y_offset)
        self.move_delete_button(rect1, x + x_offset, y + y_offset)

    def spawn_rectangle(self):
        x1, y1 = 50, 50
        x2, y2 = 150, 150
        new_rectangle = SnappableRectangle(self.canvas, x1, y1, x2, y2, "green", self)
        self.rectangles.append(new_rectangle)
        self.delete_buttons[new_rectangle.rect] = new_rectangle.delete_button
        self.canvas.create_window((x1, y1), window=new_rectangle.delete_button, anchor=tk.NW)

        #TODO: priradit k rectanglu konkretni soubor i s ikonkou
        try:
            new_rectangle.associated_file = filedialog.askopenfilename()
        except:
            new_rectangle.delete_rectangle()

    def move_delete_button(self, delete_buttons, rect, x, y):
        if rect in delete_buttons:
            delete_button = delete_buttons[rect]
            bbox = self.canvas.bbox(rect)
            self.canvas.create_window((bbox[0] + x, bbox[1] + y), window=delete_button, anchor=tk.NW)

    def get_token(self):
        while True:
            token = simpledialog.askstring("Token Dialog", "Enter your bot token:")
            if not token:
                self.withdraw()
                self.destroy()
                exit()
            else:
                self.token = token
                break
    
    def send_token(self):
        global predavaci_fronta
        predavaci_fronta.put(self.token)

# Queue functions start here

class Queue_extended(Queue):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Queue_extended, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, maxsize=9999):
        super().__init__(maxsize)

def global_receive_from_queue(): # takhle debilne to je napsany kvuli konkurenci
                                 # normalnejsi by bylo neco jako q.get(timeout=999999)
    q = Queue_extended()
    while True:
        try:
            data_to_transfer = q.get(timeout=1)
            return data_to_transfer
        except ERROR_QUEUE_EMPTY:
            pass # intentional pass

# Non-queue functions connecting TKinter and Discord Bot start here

def start_bot_and_tkinter_concurrently():
    tkinter_thread = threading.Thread(target=tkinter_start_mainloop)
    bot_thread = threading.Thread(target=discord_bot_loop)

    tkinter_thread.start()
    # zde probehne predani tokenu pomoci fronty
    bot_thread.start()

    # tkinter_thread.join()
    # bot_thread.join()

def tkinter_start_mainloop():
    root = Tk_extended()
    root.title("Cog Control")

    root.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    root.canvas.pack()

    core_rectangle = SnappableRectangle(root.canvas, 100, 100, 200, 200, "blue", root)
    root.rectangles.append(core_rectangle)

    root.canvas.bind("<ButtonPress-1>", root.on_click)
    root.canvas.bind("<B1-Motion>", root.on_drag)

    spawn_button = tk.Button(root, text="Spawn Rectangle", command=root.spawn_rectangle)
    spawn_button.pack()

    root.get_token()
    root.send_token()

    root.mainloop()

if __name__ == '__main__':
    global predavaci_fronta
    predavaci_fronta = Queue_extended()
    start_bot_and_tkinter_concurrently()