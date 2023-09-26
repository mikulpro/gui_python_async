from tkinter import filedialog, Canvas, Button, Tk, N, NW, W, SW, S, SE, E, NE, CENTER
import os, random, threading
from sender import send_command
from math import sqrt

# konstanty pro snapovani bloku
ACTIVE_BACKGROUND_BUTTON_COLOR = "black"
BUTTON_PADDING_Y = 3
BUTTON_WIDTH = 30
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 500
RECTANGLE_SIDE_SIZE = 125 # bohuzel nemuze byt abecedne
SNAP_TRESHOLD = 50
COG_ACTIVATION_DISTANCE_MAX = RECTANGLE_SIDE_SIZE+SNAP_TRESHOLD
DELTE_BUTTON_OFFSET = 10
DEFAULT_CELL_SIZE = COG_ACTIVATION_DISTANCE_MAX
CORE_SIDE_SIZE = RECTANGLE_SIDE_SIZE # zatim blbne, kdyz je jiny nez RECTANGLE_SIDE_SIZE
EDGE_ZONE_SIZE = RECTANGLE_SIDE_SIZE+10
FONT_SIZE_BUTTONS = 12
FONT_SIZE_RECTANGLES = 14
FONT_FAMILY = "Arial"
UNSNAP_TRESHOLD = 30
# FONT_FAMILY jsou "Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode", "Palatino Linotype", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"

# konstanty pro bota
COG_ACTIVATION_PATH = "cogs/activation.csv"

class _SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill, input_root):
        self.associated_file = None
        self.bottom = None
        self.canvas = canvas
        self.center = [int((x1+x2)/2), int((y1+y2)/2)]
        self.delete_button = Button(canvas, text="X", command=self.delete)
        self.is_active = False
        self.last_pos = (abs(x2-x1), abs(y2-y1))
        self.left = None
        self.name = None
        self.original_pos = (abs(x2-x1), abs(y2-y1))
        self.path = None
        self.prev_x = 0
        self.prev_y = 0
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, tags="rectangle")
        self.right = None
        self.root = input_root
        self.snap_distance = SNAP_TRESHOLD
        self.tag = str(self.root.get_id())
        self.text_center = [int((x1+x2)/2), int((y1+y2)/2)]
        self.text_string = "PLACE_HOLDER"
        self.text_object = self.canvas.create_text(self.text_center[0], self.text_center[1], text=self.text_string, font=(FONT_FAMILY, FONT_SIZE_RECTANGLES), fill="white")
        self.top = None
        self.unsnap_force = UNSNAP_TRESHOLD
        self.window_id = None

        # pohyb vykresleneho ctverce
        self.canvas.tag_bind(self.rect, '<ButtonPress-1>', self.start_drag)
        self.canvas.tag_bind(self.rect, '<B1-Motion>', self.drag)
        self.canvas.tag_bind(self.rect, '<ButtonRelease-1>', self.stop_drag)

        # pohyb vykresleneho napisu na ctverci
        self.canvas.tag_bind(self.text_object, '<ButtonPress-1>', self.start_drag)
        self.canvas.tag_bind(self.text_object, '<B1-Motion>', self.drag)
        self.canvas.tag_bind(self.text_object, '<ButtonRelease-1>', self.stop_drag)

        # pohyb delete buttonu
        self.canvas.bind(self.delete_button, '<ButtonPress-1>', self.start_drag)
        self.canvas.bind(self.delete_button, '<B1-Motion>', self.drag)
        self.canvas.bind(self.delete_button, '<ButtonRelease-1>', self.stop_drag)

        self.canvas.latest_rectangle = self

    def add_name_and_path(self):
            self.path = filedialog.askopenfilename(title="Select Valid Discord Cog File", initialdir="storage/", filetypes=(("Discord Cog", "*.py"),))
            if not self.path:
                return
            self.name = os.path.basename(self.path)
            self.name, _ = os.path.splitext(self.name)

            # aktualizace labelu
            if self.name:
                self.text_string = str(self.name)
            else:
                self.text_string = "NAME_ERROR"
            self.canvas.itemconfig(self.text_object, text=self.text_string)

    def as_dict(self):
        return {'left': self.left, 'right': self.right, 'top': self.top, 'bottom': self.bottom}

    def delete(self):
        for rectangle in self.root.rectangles:
            if rectangle == self:
                try:
                    if rectangle is not None and rectangle.name != "None" and rectangle.name is not None:
                        self.root.deactivate_cog(rectangle.name)
                except: ...
                try:
                    self.canvas.delete(rectangle.text_object)
                    self.canvas.delete(rectangle.rect)
                except: ...
    
    def drag(self, event):
        dx = event.x - self.last_pos[0]
        dy = event.y - self.last_pos[1]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text_object, dx, dy)
        #self.canvas.move(self.delete_button, dx, dy)
        self.last_pos = (event.x, event.y)

    def start_drag(self, event):
        self.original_pos = self.canvas.coords(self.rect)[:2]
        self.last_pos = (event.x, event.y)

    def stop_drag(self, event):
        self.update_center()
          
    def update_center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.center = [int((x1+x2)/2), int((y1+y2)/2)]
        self.text_center = self.center
        self.canvas.coords(self.text_object, self.text_center[0], self.text_center[1])
        #self.canvas.coords(self.delete_button, (self.text_center[0]-(int(RECTANGLE_SIDE_SIZE/2))+DELTE_BUTTON_OFFSET), (self.text_center[1]-(int(RECTANGLE_SIDE_SIZE/2))+DELTE_BUTTON_OFFSET))

class Tk_extended(Tk):
    def __init__(self, *args, **kwargs):
        # dedicnost
        super().__init__(*args, **kwargs)       
        
        # setup promennych
        self.number_of_deleted_rectangles = 0
        self.number_of_rectangles = 0
        self.rectangles = []
        self.last_id = 0
        self.last_rectangle = None
        self.lock = threading.Lock()

        # setup inteligentnich objektu
        self.canvas = Canvas(self, bg="white", width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.core = _SnappableRectangle(canvas=self.canvas, x1=EDGE_ZONE_SIZE, y1=EDGE_ZONE_SIZE, x2=EDGE_ZONE_SIZE+CORE_SIDE_SIZE, y2=EDGE_ZONE_SIZE+CORE_SIDE_SIZE, fill="black", input_root=self)
        self.core.canvas.itemconfig(self.core.text_object, text="CORE")
        self.rectangles.append(self.core)
        self.canvas.after(200, lambda: self.draw_grid())

    def activate_cog(self, cog):
        threading.Thread(target=self.task(cog, "Load")).start()

    def deactivate_cog(self, cog):
        threading.Thread(target=self.task(cog, "Unload")).start()

    def delete_last_rectangle(self):
        index = self.number_of_rectangles - self.number_of_deleted_rectangles
        print(f"Attempting to delete rectangle with index {index}")
        
        if index > 0 and index < len(self.rectangles):
            self.canvas.delete(self.rectangles[index].text_object)
            self.canvas.delete(self.rectangles[index].rect)
            self.number_of_deleted_rectangles += 1

    def delete_every_rectangle(self):
        for rectangle in self.rectangles:
            if rectangle != self.core:
                try:
                    if rectangle is not None and rectangle.name != "None" and rectangle.name is not None:
                        self.deactivate_cog(rectangle.name)
                except: ...
                try:
                    self.canvas.delete(rectangle.text_object)
                    self.canvas.delete(rectangle.rect)
                except: ...
        self.rectangles = [self.core]
        self.number_of_rectangles = 0
        self.number_of_deleted_rectangles = 0
        self.last_rectangle = None

    def does_overlap(self, rect1, rect2):
        ax, ay = rect1.center
        bx, by = rect2.center
        
        # kontrola levo, pravo
        if ax > (bx+RECTANGLE_SIDE_SIZE+UNSNAP_TRESHOLD) or ax < (bx-RECTANGLE_SIDE_SIZE-UNSNAP_TRESHOLD):
            return False
            
        # kontrola nahoru, dolu
        if ay > (by+RECTANGLE_SIDE_SIZE+UNSNAP_TRESHOLD) or ay < (by-RECTANGLE_SIDE_SIZE-UNSNAP_TRESHOLD):
            return False
            
        return True

    def drag_rectangle(self, event):
        closest = self.closest_tag(self.canvas, event.x, event.y)

        if "draggable" in self.canvas.gettags(closest):
            self.canvas.move(closest, event.x - self.canvas.coords(closest)[0], event.y - self.canvas.coords(closest)[1])
            if self.is_snapped_to_core(closest):
                self.canvas.itemconfig(closest, fill="green")
            else:
                self.canvas.itemconfig(closest, fill="blue")
    
    def draw_grid(self):
        canvas = self.canvas
        cell_size = DEFAULT_CELL_SIZE

        # svisle cary
        for x in range(0, canvas.winfo_width(), cell_size):
            canvas.create_line(x, 0, x, canvas.winfo_height(), fill='lightgray')
        
        # vodorovne cary
        for y in range(0, canvas.winfo_height(), cell_size):
            canvas.create_line(0, y, canvas.winfo_width(), y, fill='lightgray')
        
        # prenos CORE do popredi
        canvas.tag_raise(self.core.rect)
        canvas.tag_raise(self.core.text_object)

    def get_id(self):
        self.last_id += 1
        return self.last_id
    
    def get_nearby_rectangles(self, caller, wanted_distance=COG_ACTIVATION_DISTANCE_MAX):
        temp = []
        for item in self.rectangles:
            if item == caller or item in temp:
                continue
            else:
                real_distance = int(sqrt((item.center[0]-caller.center[0])**2 + (item.center[1]-caller.center[1])**2))
                if real_distance <= wanted_distance:
                    temp.append(item)
        return temp

    def load_setup_to_discord_bot(self):
        near_core = self.get_nearby_rectangles(caller=self.core)
        for near_cog in near_core:
            if near_cog not in near_core:
                near_core.append(near_cog)
            for far_cog in self.get_nearby_rectangles(caller=near_cog):
                if far_cog not in near_core:
                    near_core.append(far_cog)
        
        cogs_to_activate = near_core.copy()
        cogs_to_deactivate = self.rectangles.copy()
        
        for cog in near_core:
            try: cogs_to_deactivate.remove(cog)
            except: ...
        
        for item in cogs_to_deactivate:
            if item is not None and item.name != "None" and item.name is not None:
                self.deactivate_cog(item.name)
        
        for item in cogs_to_activate:
            if item is not None and item.name != "None" and item.name is not None:
                self.activate_cog(item.name)

    def mainloop_extended(self):
        self.tkinter_extended_setup_function()
        super().mainloop()

    def spawn_rectangle(self):
        x1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
        y1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))
        x2, y2 = x1+RECTANGLE_SIDE_SIZE, y1+RECTANGLE_SIDE_SIZE
        temp = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill=str(self.get_random_color()), input_root=self)
        temp.update_center()

        _overlap_issues = True
        while _overlap_issues:
            for other_rectangle in self.rectangles:
                if self.does_overlap(temp, other_rectangle):
                    temp.delete()
                    x1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
                    y1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))
                    x2, y2 = x1+RECTANGLE_SIDE_SIZE, y1+RECTANGLE_SIDE_SIZE
                    temp = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill=str(self.get_random_color()), input_root=self)
                    temp.update_center()
                    _overlap_issues = True
                    continue
                else:
                    _overlap_issues = False

        temp.add_name_and_path()
        self.rectangles.append(temp)
        self.number_of_rectangles += 1

        return temp

    def task(self, file_name, status):
        with self.lock:
            succ = send_command(f"{status} cogs.{file_name}")

    def tkinter_extended_setup_function(self):
        self.title("Discord Cog Manager")
        
        self.canvas.pack(pady=20, padx=20)
        self.canvas.bind("<B1-Motion>", self.drag_rectangle)

        spawn_button = Button(self, text="Load Setup to Discord Bot", command=self.load_setup_to_discord_bot, font=(FONT_FAMILY, FONT_SIZE_BUTTONS), width=BUTTON_WIDTH, activebackground=ACTIVE_BACKGROUND_BUTTON_COLOR)
        spawn_button.pack(pady=BUTTON_PADDING_Y)

        spawn_button = Button(self, text="Spawn Rectangle", command=self.spawn_rectangle, font=(FONT_FAMILY, FONT_SIZE_BUTTONS), width=BUTTON_WIDTH, activebackground=ACTIVE_BACKGROUND_BUTTON_COLOR)
        spawn_button.pack(pady=BUTTON_PADDING_Y)

        delete_button = Button(self, text="Delete Last Rectangle", command=self.delete_last_rectangle, font=(FONT_FAMILY, FONT_SIZE_BUTTONS), width=BUTTON_WIDTH, activebackground=ACTIVE_BACKGROUND_BUTTON_COLOR)
        delete_button.pack(pady=BUTTON_PADDING_Y)

        supreme_delete_button = Button(self, text="Delete Everything Except CORE", command=self.delete_every_rectangle, font=(FONT_FAMILY, FONT_SIZE_BUTTONS), width=BUTTON_WIDTH, activebackground=ACTIVE_BACKGROUND_BUTTON_COLOR)
        supreme_delete_button.pack(pady=BUTTON_PADDING_Y)

    @staticmethod
    def closest_tag(canvas, x, y):
        min_distance = float("inf")
        closest_item = None

        for item in canvas.find_all():
            coords = canvas.coords(item)
            for i in range(0, len(coords), 2):
                item_x = coords[i]
                item_y = coords[i+1]
                
                distance = ((x - item_x)**2 + (y - item_y)**2)**0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_item = item

        return closest_item
    
    @staticmethod
    def get_random_color():
        return "#{:06x}".format(random.randint(0, 0x7F7F7F))

if __name__ == "__main__":
    GUI = Tk_extended()
    GUI.mainloop_extended()