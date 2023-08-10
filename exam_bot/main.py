import tkinter as tk
from tkinter import simpledialog, filedialog
from bot_core import BotCore
import asyncio
import threading

# konstanty pro snapovani bloku
TRESHOLD = 5
CANVAS_WIDTH = 1700
CANVAS_HEIGHT = 900

class SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill):
        self.canvas = canvas
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, tags="rectangle")
        self.connected_rectangles = []
        self.delete_button = tk.Button(canvas, text="Delete", command=self.delete_rectangle)
        self.associated_file = None
        self.is_active = False

    def delete_rectangle(self):
        #TODO: odstranit pripojeny soubor ze slozky pro cogy
        for rect in self.connected_rectangles:
            rect.connected_rectangles.remove(self)
        self.canvas.delete(self.rect)
        self.delete_button.destroy()

def on_click(event):
    global prev_x, prev_y, selected_rectangle
    prev_x, prev_y = event.x, event.y
    selected_rectangle = canvas.find_closest(event.x, event.y)[0]

def on_drag(event):
    global prev_x, prev_y
    x, y = event.x - prev_x, event.y - prev_y
    if selected_rectangle:
        snapped_rect = snap_together(selected_rectangle, x, y)
        if snapped_rect:
            selected_rectangle.is_active = True
            align_rectangles(selected_rectangle, snapped_rect, x, y)
        else:
            selected_rectangle.is_active = False
            canvas.move(selected_rectangle, x, y)
            move_delete_button(selected_rectangle, x, y)
    prev_x, prev_y = event.x, event.y

def snap_together(rect, x, y):
    threshold = TRESHOLD  # Adjust this value to control the snap sensitivity
    bbox = canvas.bbox(rect)

    for other_rect in rectangles:
        if other_rect.rect != rect:
            other_bbox = canvas.bbox(other_rect.rect)
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

def align_rectangles(rect1, rect2, x, y):
    bbox1 = canvas.bbox(rect1)
    bbox2 = canvas.bbox(rect2)

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

    canvas.move(rect1, x + x_offset, y + y_offset)
    move_delete_button(rect1, x + x_offset, y + y_offset)

def spawn_rectangle():
    x1, y1 = 50, 50
    x2, y2 = 150, 150
    new_rectangle = SnappableRectangle(canvas, x1, y1, x2, y2, "green")
    rectangles.append(new_rectangle)
    delete_buttons[new_rectangle.rect] = new_rectangle.delete_button
    canvas.create_window((x1, y1), window=new_rectangle.delete_button, anchor=tk.NW)

    #TODO: priradit k rectanglu konkretni soubor i s ikonkou
    try:
        new_rectangle.associated_file = filedialog.askopenfilename()
    except:
        new_rectangle.delete_rectangle()

def move_delete_button(rect, x, y):
    if rect in delete_buttons:
        delete_button = delete_buttons[rect]
        bbox = canvas.bbox(rect)
        canvas.create_window((bbox[0] + x, bbox[1] + y), window=delete_button, anchor=tk.NW)

async def get_token():
    while True:
        token = simpledialog.askstring("Token Dialog", "Enter your bot token:")
        if not token:
            root.withdraw()
            root.destroy()
            exit()
        else:
            return token

async def run_bot_in_background(token):
    discord_bot = BotCore(token)
    await discord_bot.run()

def start_bot_in_background(token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_in_background(token))
    loop.close()

def start_bot_and_tkinter_concurrently():
    token = asyncio.run(get_token())
    threading.Thread(target=start_bot_in_background, args=(token,)).start()
    root.mainloop()
    
###############################################################################################

root = tk.Tk()
root.title("Bot Cog Manager")

canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack()

core_rectangle = SnappableRectangle(canvas, 100, 100, 200, 200, "blue")

global rectangles
rectangles = [core_rectangle]
delete_buttons = {}
selected_rectangle = None

canvas.bind("<ButtonPress-1>", on_click)
canvas.bind("<B1-Motion>", on_drag)

spawn_button = tk.Button(root, text="Spawn Rectangle", command=spawn_rectangle)
spawn_button.pack()

start_bot_and_tkinter_concurrently()