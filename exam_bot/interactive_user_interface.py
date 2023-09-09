from tkinter import filedialog, Canvas, Button, Tk, N, NW, W, SW, S, SE, E, NE, CENTER
from core import runni_bota, vypni_bota
import shutil, os, csv, random, threading
from sender import send_command

# konstanty pro snapovani bloku
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700
SNAP_TRESHOLD = 15
RECTANGLE_SIDE_SIZE = 100
CORE_SIDE_SIZE = RECTANGLE_SIDE_SIZE # zatim blbne, kdyz je jiny nez RECTANGLE_SIDE_SIZE
EDGE_ZONE_SIZE = RECTANGLE_SIDE_SIZE+10
FONT_SIZE = 18
FONT_FAMILY = "Arial"
UNSNAP_TRESHOLD = 30
# FONT_FAMILY jsou "Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode", "Palatino Linotype", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"

# konstanty pro bota
COG_ACTIVATION_PATH = "cogs/activation.csv"

class _SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill, input_root, show_delete=True, tags=None):
        self.associated_file = None
        self.bottom = None
        self.canvas = canvas
        self.delete_button = None
        self.delete_button_id = None
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
        self.tags = tags
        self.top = None
        self.unsnap_force = UNSNAP_TRESHOLD
        self.window_id = None

        self.canvas.tag_bind(self.rect, '<ButtonPress-1>', self.start_drag)
        self.canvas.tag_bind(self.rect, '<B1-Motion>', self.drag)
        self.canvas.tag_bind(self.rect, '<ButtonRelease-1>', self.stop_drag)

    def add_name_and_path(self):
            self.path = filedialog.askopenfilename(title="Select Valid Discord Cog File", initialdir="storage/", filetypes=(("Discord Cog", "*.py"),))
            while True:
                if self.path is not None:
                    break
            self.name = os.path.basename(self.path)
            self.name, _ = os.path.splitext(self.name)
            print(self.name)

    def as_dict(self):
        return {'left': self.left, 'right': self.right, 'top': self.top, 'bottom': self.bottom}

    def delete(self):
        self.canvas.delete(self.rect)
        
        if self.delete_button:
            self.delete_button.destroy()
            self.canvas.delete(self.window_id)

        if self in self.root.rectangles:
            self.root.rectangles.remove(self)
        
        if self.rect in self.root.delete_buttons:
            del self.root.delete_buttons[self.rect]
    
    def drag(self, event):
        dx = event.x - self.last_pos[0]
        dy = event.y - self.last_pos[1]
        self.canvas.move(self.rect, dx, dy)
        self.last_pos = (event.x, event.y)

        for other_rect in self.canvas.find_withtag('draggable'):
            if other_rect != self.rect:
                self.snap_to(other_rect)

    def is_close_to(self, other_rect):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        ox1, oy1, ox2, oy2 = self.canvas.coords(other_rect)

        close_left = abs(x2 - ox1) <= self.snap_distance
        close_right = abs(x1 - ox2) <= self.snap_distance
        close_top = abs(y1 - oy2) <= self.snap_distance
        close_bottom = abs(y2 - oy1) <= self.snap_distance

        return close_left, close_right, close_top, close_bottom

    def snap_to(self, other_rect):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        ox1, oy1, ox2, oy2 = self.canvas.coords(other_rect)

        close_left, close_right, close_top, close_bottom = self.is_close_to(other_rect)

        if close_left:
            self.canvas.move(self.rect, ox1 - x2, 0)
            self.left = other_rect
        elif close_right:
            self.canvas.move(self.rect, ox2 - x1, 0)
            self.right = other_rect
        elif close_top:
            self.canvas.move(self.rect, 0, oy2 - y1)
            self.top = other_rect
        elif close_bottom:
            self.canvas.move(self.rect, 0, oy1 - y2)
            self.bottom = other_rect

        new_x, new_y = self.canvas.coords(self.rect)[:2]
        distance_moved = ((new_x - self.original_pos[0])**2 + (new_y - self.original_pos[1])**2)**0.5
        if (self.left or self.right or self.top or self.bottom) and distance_moved > self.unsnap_force:
            self.left, self.right, self.top, self.bottom = None, None, None, None
            self.canvas.move(self.rect, self.original_pos[0] - new_x, self.original_pos[1] - new_y)

    def start_drag(self, event):
        self.last_pos = (event.x, event.y)
        self.original_pos = self.canvas.coords(self.rect)[:2]

    def stop_drag(self, event):
        self.left, self.right, self.top, self.bottom = None, None, None, None

class Tk_extended(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)       
        self.canvas = None
        self.core = None
        self.last_rectangle = None
        self.rectangles = []

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

    def delete_rectangle(self):
        if self.last_rectangle:
            self.canvas.delete(self.last_rectangle)
            self.last_rectangle = None

    def drag_rectangle(self, event):
        closest = self.closest_tag(self.canvas, event.x, event.y)

        if "draggable" in self.canvas.gettags(closest):
            self.canvas.move(closest, event.x - self.canvas.coords(closest)[0], event.y - self.canvas.coords(closest)[1])
            if self.is_snapped_to_core(closest):
                self.canvas.itemconfig(closest, fill="green")
            else:
                self.canvas.itemconfig(closest, fill="blue")

    def is_snapped_to_core(self, rectangle):
        r_coords = self.canvas.coords(rectangle)
        core_coords = self.canvas.coords(self.core_rectangle)
        
        horizontal_snapped = r_coords[2] == core_coords[0] or r_coords[0] == core_coords[2]
        vertical_snapped = r_coords[3] == core_coords[1] or r_coords[1] == core_coords[3]
        
        return horizontal_snapped or vertical_snapped

    def mainloop_extended(self):
        self.tkinter_extended_setup_function()
        super().mainloop()

    def spawn_rectangle(self, is_core=False):
        x1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
        y1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))

        while self.does_overlap(x1, y1, EDGE_ZONE_SIZE+SNAP_TRESHOLD, EDGE_ZONE_SIZE+SNAP_TRESHOLD, self.rectangles):
            x1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
            y1 = random.randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))

        x2, y2 = x1+CORE_SIDE_SIZE, y1+CORE_SIDE_SIZE
        new_rectangle = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill="white", input_root=self, show_delete=False, tags=("draggable",))

        if is_core:
            new_rectangle.fill = "black"
            new_rectangle.show_delete = False
            self.core = new_rectangle
        else:
            x2, y2 = x1+RECTANGLE_SIDE_SIZE, y1+RECTANGLE_SIDE_SIZE
            new_rectangle.fill = self.get_random_color()
            new_rectangle.add_name_and_path()
        
        return new_rectangle

    def tkinter_extended_setup_function(self):
        TKe = self
        TKe.title("Discord Cog Manager")
        TKe.canvas = Canvas(TKe, bg="white", width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        TKe.canvas.pack(pady=20, padx=20)

        self.core = TKe.spawn_rectangle(is_core=True)
        self.canvas.bind("<B1-Motion>", self.drag_rectangle)

        spawn_button = Button(TKe, text="Spawn Rectangle", command=TKe.spawn_rectangle, font=(FONT_FAMILY, FONT_SIZE))
        spawn_button.pack(pady=10)

        delete_button = Button(TKe, text="Delete Last Rectangle", command=TKe.delete_rectangle, font=(FONT_FAMILY, FONT_SIZE))
        delete_button.pack(pady=10)

    @staticmethod
    def activate_cog(cog):
        print(f"Load cogs.{cog}")
        send_command(f"Load cogs.{cog}")

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
    def deactivate_cog(cog):
        print(f"Unload cogs.{cog}")
        send_command(f"Unload cogs.{cog}")

    @staticmethod
    def does_overlap(x1, y1, width, height, rectangles):
        left = x1 - width/2
        right = x1 + width/2
        top = y1 - height/2
        bottom = y1 + height/2
        
        for rect in rectangles:
            rect_dict = rect.as_dict()
            if (left < rect_dict['right'] and right > rect_dict['left'] and
                top < rect_dict['bottom'] and bottom > rect_dict['top']):
                return True

        return False
    
    @staticmethod
    def get_random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

if __name__ == "__main__":
    GUI = Tk_extended()
    GUI.mainloop_extended()