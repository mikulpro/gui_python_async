from tkinter import simpledialog, filedialog, Canvas, Button, Tk, N, NW, W, SW, S, SE, E, NE, CENTER
from random import choice, uniform, randint

# konstanty pro snapovani bloku
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 900
SNAP_TRESHOLD = 6
RECTANGLE_SIDE_SIZE = 100
CORE_SIDE_SIZE = RECTANGLE_SIDE_SIZE # zatim blbne, kdyz je jiny nez RECTANGLE_SIDE_SIZE
EDGE_ZONE_SIZE = RECTANGLE_SIDE_SIZE+10
FONT_SIZE = 32
FONT_FAMILY =  "Helvetica"
# FONT_FAMILY jsou "Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode", "Palatino Linotype", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"

class _SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill, input_root, show_delete=True):
        self.associated_file = None
        self.canvas = canvas
        self.connected_rectangles = []
        self.delete_button = None
        self.delete_button_id = None
        self.is_active = False
        self.prev_x = 0
        self.prev_y = 0
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, tags="rectangle")
        self.root = input_root
        self.window_id = None
        
        if show_delete:
            self.delete_button = Button(master=self.canvas, text="COG", command=lambda: self.root.delete_rectangle(self))
            self.window_id = self.canvas.create_window((x1 + (x2-x1)/2, y1 + (y2-y1)/2), window=self.delete_button, anchor=CENTER)

        if not show_delete:
            self.delete_button = Button(master=self.canvas, text="CORE", height=0, width=0, state='disabled', command=lambda: self.root.delete_rectangle(self))
            self.window_id = self.canvas.create_window((x1 + (x2-x1)/2, y1 + (y2-y1)/2), window=self.delete_button, anchor=CENTER)

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
        super().__init__(*args, **kwargs)  # Assuming you're extending a parent class. If not, remove this line.
        self.canvas = None
        self.delete_buttons = {}
        self.rectangles = []
        self.rect_to_button_id_dict = {}
        self.selected_rectangle = None
        self.token = None

    def delete_rectangle(self, rectangle_obj):
        rectangle_obj.delete()    
        #TODO: odstranit pripojeny soubor ze slozky pro cogy

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
        if self.selected_rectangle:
            snapped_rect_obj = self.snap_together(self.selected_rectangle, dx, dy)
            if snapped_rect_obj:
                self.selected_rectangle.is_active = True
                self.align_rectangles(self.selected_rectangle, snapped_rect_obj, dx, dy)
            else:
                self.selected_rectangle.is_active = False
                self.canvas.move(self.selected_rectangle.rect, dx, dy)
                self.move_delete_button(self.selected_rectangle, dx, dy)
        self.prev_x, self.prev_y = event.x, event.y

        if snapped_rect_obj:
            if self.can_unsnap(self.selected_rectangle, snapped_rect_obj, dx, dy):
                self.selected_rectangle.is_active = False
                self.canvas.move(self.selected_rectangle.rect, dx, dy)
                self.move_delete_button(self.selected_rectangle, dx, dy)
            else:
                self.selected_rectangle.is_active = True
                self.align_rectangles(self.selected_rectangle, snapped_rect_obj, dx, dy)
        else:
            self.selected_rectangle.is_active = False
            self.canvas.move(self.selected_rectangle.rect, dx, dy)
            self.move_delete_button(self.selected_rectangle, dx, dy)

    def snap_together(self, rect, x, y):
        bbox = self.canvas.bbox(rect.rect)

        for other_rect in self.rectangles:
            if other_rect.rect != rect.rect:
                other_bbox = self.canvas.bbox(other_rect.rect)
                if other_bbox:
                    
                    x_distance_left = abs(bbox[0] - other_bbox[2])
                    x_distance_right = abs(bbox[2] - other_bbox[0])
                    y_distance_top = abs(bbox[1] - other_bbox[3])
                    y_distance_bottom = abs(bbox[3] - other_bbox[1])

                    if x_distance_left < SNAP_TRESHOLD and 0 < y_distance_bottom < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]):
                        return other_rect
                    elif x_distance_right < SNAP_TRESHOLD and 0 < y_distance_top < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]):
                        return other_rect
                    elif y_distance_top < SNAP_TRESHOLD and 0 < x_distance_right < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]):
                        return other_rect
                    elif y_distance_bottom < SNAP_TRESHOLD and 0 < x_distance_left < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]):
                        return other_rect
        return None

    def align_rectangles(self, rect1, rect2, x, y):      
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

        self.canvas.move(rect2.rect, x, y)
        self.move_delete_button(rect2, x, y)

    def spawn_rectangle(self, is_core=False):
        x1 = randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
        y1 = randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))

        if is_core:
            x2, y2 = x1+CORE_SIDE_SIZE, y1+CORE_SIDE_SIZE
            new_rectangle = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill="red", input_root=self, show_delete=False)
        else:
            x2, y2 = x1+RECTANGLE_SIDE_SIZE, y1+RECTANGLE_SIDE_SIZE
            new_rectangle = _SnappableRectangle(canvas=self.canvas, x1=x1, y1=y1, x2=x2, y2=y2, fill="grey", input_root=self, show_delete=True)
        self.delete_buttons[new_rectangle.rect] = new_rectangle.window_id
        self.rect_to_button_id_dict[new_rectangle] = new_rectangle.window_id
        self.rectangles.append(new_rectangle)

        #TODO: priradit k rectanglu konkretni soubor i s ikonkou

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
            return True

        return False
    
##############################################################################################################

def tkinter_extended_start():
    TKe = Tk_extended()
    TKe.title("Cog Control")
    TKe.canvas = Canvas(TKe, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    TKe.canvas.pack()

    TKe.spawn_rectangle(is_core=True)
    TKe.canvas.bind("<ButtonPress-1>", TKe.on_click)
    TKe.canvas.bind("<B1-Motion>", TKe.on_drag)

    spawn_button = Button(TKe, text="Spawn Rectangle", command=TKe.spawn_rectangle, font=(FONT_FAMILY, FONT_SIZE))
    spawn_button.pack()

    TKe.mainloop()

if __name__ == "__main__":
    tkinter_extended_start()