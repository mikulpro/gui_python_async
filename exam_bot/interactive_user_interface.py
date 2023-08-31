from tkinter import filedialog, Canvas, Button, Tk, N, NW, W, SW, S, SE, E, NE, CENTER
from core import runni_bota, vypni_bota
import shutil, os, csv, random, threading

# konstanty pro snapovani bloku
CANVAS_WIDTH = 1400
CANVAS_HEIGHT = 1000
SNAP_TRESHOLD = 20
RECTANGLE_SIDE_SIZE = 100
CORE_SIDE_SIZE = RECTANGLE_SIDE_SIZE # zatim blbne, kdyz je jiny nez RECTANGLE_SIDE_SIZE
EDGE_ZONE_SIZE = RECTANGLE_SIDE_SIZE+10
FONT_SIZE = 32
FONT_FAMILY = "Arial"
# FONT_FAMILY jsou "Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode", "Palatino Linotype", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"

# konstanty pro bota
COG_ACTIVATION_PATH = "cogs/activation.csv"

class _SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill, input_root, show_delete=True):
        self.associated_file = None
        self.canvas = canvas
        self.connected_rectangles = []
        self.delete_button = None
        self.delete_button_id = None
        self.is_active = False
        self.name = None
        self.path = None
        self.prev_x = 0
        self.prev_y = 0
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, tags="rectangle")
        self.root = input_root
        self.snapped_to = []
        self.window_id = None
        
        if show_delete:
            self.delete_button = Button(master=self.canvas, text="COG", command=lambda: self.root.delete_rectangle(self))
            self.window_id = self.canvas.create_window((x1 + (x2-x1)/2, y1 + (y2-y1)/2), window=self.delete_button, anchor=CENTER)

        if not show_delete:
            self.delete_button = Button(master=self.canvas, text="CORE", height=0, width=0, state='disabled', command=lambda: self.root.delete_rectangle(self))
            self.window_id = self.canvas.create_window((x1 + (x2-x1)/2, y1 + (y2-y1)/2), window=self.delete_button, anchor=CENTER)

    def add_name_and_path(self):
            self.path = filedialog.askopenfilename(title="Glory Hole", initialdir="storage/", filetypes=(("Long Cocks", "*.py"),))
            while True:
                if self.path is not None:
                    break
            self.name = os.path.basename(self.path)
            self.name, _ = os.path.splitext(self.name)

    def delete(self):
        # Delete rectangle from canvas
        self.canvas.delete(self.rect)
        
        # Delete associated delete button
        if self.delete_button:
            self.delete_button.destroy()
            self.canvas.delete(self.window_id)

        # Remove from root's rectangle list
        if self in self.root.rectangles:
            self.root.rectangles.remove(self)
        
        # Remove from delete_buttons dictionary
        if self.rect in self.root.delete_buttons:
            del self.root.delete_buttons[self.rect]

class Tk_extended(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = None
        self.delete_buttons = {}
        self.rectangles = []
        self.rect_to_button_id_dict = {}
        self.selected_rectangle = None
        self.token = None
        self.core = None

    def mainloop_extended(self):
        #runni_bota()
        self.tkinter_extended_setup_function()
        super().mainloop()
        #vypni_bota()

    def delete_rectangle(self, rectangle_obj):
        rectangle_obj.delete()

    def on_click(self, event):
        self.prev_x = event.x
        self.prev_y = event.y
        rect_id = self.canvas.find_closest(event.x, event.y)[0]
        for rect_obj in self.rectangles:
            if rect_obj.rect == rect_id:
                self.selected_rectangle = rect_obj
                break

    def on_drag(self, event):
        dx, dy = event.x - self.prev_x, event.y - self.prev_y
        
        if not self.selected_rectangle:
            self.prev_x, self.prev_y = event.x, event.y
            return

        # Check for snapping
        snapped_rect_objs = self.snap_together(self.selected_rectangle, event.x, event.y)
        
        # If there are rectangles to snap with
        if snapped_rect_objs:
            for snapped_rect_obj in snapped_rect_objs:
                # If not already snapped
                if not self.selected_rectangle.is_active:
                    # Snap together
                    self.align_rectangles(self.selected_rectangle, snapped_rect_obj, dx, dy)
                    self.selected_rectangle.is_active = True
                else:
                    # Check for unsnapping condition
                    if self.can_unsnap(self.selected_rectangle, snapped_rect_obj, dx, dy):
                        self.canvas.move(self.selected_rectangle.rect, dx, dy)
                        self.move_delete_button(self.selected_rectangle, dx, dy)
                        self.selected_rectangle.is_active = False
                    else:
                        # If still needs to be snapped
                        self.align_rectangles(self.selected_rectangle, snapped_rect_obj, dx, dy)
                        self.selected_rectangle.is_active = True
        else: # If no snapping rectangles
            self.canvas.move(self.selected_rectangle.rect, dx, dy)
            self.move_delete_button(self.selected_rectangle, dx, dy)
            self.selected_rectangle.is_active = False

        self.prev_x, self.prev_y = event.x, event.y

    def snap_together(self, rect, x, y):
        bbox = self.canvas.bbox(rect.rect)
        snapped_rects = []

        for other_rect in self.rectangles:
            if other_rect.rect != rect.rect:
                other_bbox = self.canvas.bbox(other_rect.rect)
                if other_bbox:
                    
                    x_distance_left = abs(bbox[0] - other_bbox[2])
                    x_distance_right = abs(bbox[2] - other_bbox[0])
                    y_distance_top = abs(bbox[1] - other_bbox[3])
                    y_distance_bottom = abs(bbox[3] - other_bbox[1])

                    if (x_distance_left < SNAP_TRESHOLD and 0 < y_distance_bottom < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]) or
                    x_distance_right < SNAP_TRESHOLD and 0 < y_distance_top < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]) or
                    y_distance_top < SNAP_TRESHOLD and 0 < x_distance_right < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]) or
                    y_distance_bottom < SNAP_TRESHOLD and 0 < x_distance_left < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0])):
                        rect.snapped_to.append(other_rect)
                        #other_rect.snapped_to.add(rect)
                        for item in rect.snapped_to:
                            snapped_rects.append(item)
                        return snapped_rects
        return None

    def align_rectangles(self, rect1, rect2, x, y):      
        if rect2 in rect1.snapped_to or rect1 in rect2.snapped_to:
            return
        
        if rect2 not in rect1.snapped_to:
            rect2.snapped_to.append(rect1)
        if rect1 not in rect2.snapped_to:
            rect1.snapped_to.append(rect2)        
        
        bbox1 = self.canvas.bbox(rect1.rect)
        bbox2 = self.canvas.bbox(rect2.rect)

        if bbox1 is None or bbox2 is None:
            return

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

        self.canvas.move(rect1.rect, x + x_offset, y + y_offset)
        self.move_delete_button(rect1, x + x_offset, y + y_offset)

        # self.canvas.move(rect2.rect, x, y)
        # self.move_delete_button(rect2, x, y)

        self.canvas.move(rect2.rect, x_offset, y_offset)
        self.move_delete_button(rect2, x_offset, y_offset)

        rect1.snapped_to.append(rect2)
        rect2.snapped_to.append(rect1)

        for other_rect in rect1.snapped_to:
            if other_rect != rect2:
                self.align_rectangles(rect2, other_rect)

        for other_rect in rect2.snapped_to:
            if other_rect != rect1:
                self.align_rectangles(rect1, other_rect)

    def spawn_rectangle(self, is_core=False):
        x1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
        y1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))

        if is_core:
            x2, y2 = x1+CORE_SIDE_SIZE, y1+CORE_SIDE_SIZE
            new_rectangle = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill="black", input_root=self, show_delete=False)
            self.core = new_rectangle
        else:
            x2, y2 = x1+RECTANGLE_SIDE_SIZE, y1+RECTANGLE_SIDE_SIZE
            random_color = self.get_random_color()
            new_rectangle = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill=random_color, input_root=self, show_delete=True)
            new_rectangle.add_name_and_path()
        self.delete_buttons[new_rectangle.rect] = new_rectangle.window_id
        self.rect_to_button_id_dict[new_rectangle] = new_rectangle.window_id
        self.rectangles.append(new_rectangle)

        return new_rectangle
    
    def move_delete_button(self, rect, dx, dy):
        button_id = self.get_button_id_for_rectangle(rect)
        if button_id:
            self.canvas.move(button_id, dx, dy)
        else:
            print(f"Error: No button ID found for rectangle {rect.rect}")
              
    def get_button_id_for_rectangle(self, rect):
        return self.rect_to_button_id_dict[rect]

    def get_rectangle_from_id(self, canvas_id):
        for rect in self.rectangles:
            if rect.rect == canvas_id:
                return rect
        return None
    
    def can_unsnap(self, rect1, rect2, x, y):
        bbox1 = self.canvas.bbox(rect1.rect)
        bbox2 = self.canvas.bbox(rect2.rect)
        if not bbox1 or not bbox2:
            return False

        new_bbox1 = (bbox1[0] + x, bbox1[1] + y, bbox1[2] + x, bbox1[3] + y)

        if new_bbox1[2] < bbox2[0] or new_bbox1[0] > bbox2[2] or new_bbox1[3] < bbox2[1] or new_bbox1[1] > bbox2[3]:
            if rect2 in rect1.snapped_to:
                rect1.snapped_to.remove(rect2)
            if rect1 in rect2.snapped_to:
                rect2.snapped_to.remove(rect1)
            return True

        return False
    
    def start_cog_loader(cog_loader_thread):
        cog_loader_thread.start()      

    @staticmethod
    def get_random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    @staticmethod
    def rgb_to_hex(r, g, b):
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    
    @staticmethod
    def tkinter_extended_setup_function():
        TKe = Tk_extended()
        TKe.title("Cog Control")
        TKe.canvas = Canvas(TKe, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        TKe.canvas.pack()

        TKe.spawn_rectangle(is_core=True)
        TKe.canvas.bind("<ButtonPress-1>", TKe.on_click)
        TKe.canvas.bind("<B1-Motion>", TKe.on_drag)

        spawn_button = Button(TKe, text="Spawn Rectangle", command=TKe.spawn_rectangle, font=(FONT_FAMILY, FONT_SIZE))
        spawn_button.pack()

    @staticmethod
    def activate_cog(cog):
        with open(COG_ACTIVATION_PATH, 'w', newline='\n') as file:
            writer = csv.writer(file)
            writer.writerows(cog.name)
    
    @staticmethod
    def deactivate_cog(cog):
        rows_to_keep = []

        with open(COG_ACTIVATION_PATH, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if cog.name not in row:
                    rows_to_keep.append(row)

        # Write the updated data back to the file
        with open(COG_ACTIVATION_PATH, 'w', newline='\n') as file:
            writer = csv.writer(file)
            writer.writerows(rows_to_keep)