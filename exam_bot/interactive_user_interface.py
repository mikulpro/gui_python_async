from tkinter import simpledialog, filedialog, Canvas, Button, Tk, N, NW, W, SW, S, SE, E, NE, CENTER
from random import choice, uniform, randint

# konstanty pro snapovani bloku
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000
SNAP_TRESHOLD = 5
RECTANGLE_SIDE_SIZE = 50
EDGE_ZONE_SIZE = 70

class SnappableRectangle:
    
    def __init__(self, canvas, x1, y1, x2, y2, fill, input_root):
        self.root = input_root
        self.canvas = canvas
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, tags="rectangle")
        self.connected_rectangles = []
        self.delete_button = Button(canvas, text="Delete", command=self.root.delete_rectangle)
        self.associated_file = None
        self.is_active = False

class Tk_extended(Tk):
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

        #TODO: nefunguje, nwm proc

    def snap_together(self, rect, x, y):
        global rectangles

        bbox = self.canvas.bbox(rect)

        for other_rect in rectangles:
            if other_rect.rect != rect:
                other_bbox = self.canvas.bbox(other_rect.rect)
                if other_bbox:
                    
                    x_distance_left = abs(bbox[0] - other_bbox[2])
                    x_distance_right = abs(bbox[2] - other_bbox[0])
                    y_distance_top = abs(bbox[1] - other_bbox[3])
                    y_distance_bottom = abs(bbox[3] - other_bbox[1])

                    if x_distance_left < SNAP_TRESHOLD and 0 < y_distance_bottom < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]):
                        return other_rect.rect
                    elif x_distance_right < SNAP_TRESHOLD and 0 < y_distance_top < (bbox[3] - bbox[1]) + (other_bbox[3] - other_bbox[1]):
                        return other_rect.rect
                    elif y_distance_top < SNAP_TRESHOLD and 0 < x_distance_right < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]):
                        return other_rect.rect
                    elif y_distance_bottom < SNAP_TRESHOLD and 0 < x_distance_left < (bbox[2] - bbox[0]) + (other_bbox[2] - other_bbox[0]):
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
        x1 = randint((0 + EDGE_ZONE_SIZE), (CANVAS_WIDTH - EDGE_ZONE_SIZE))
        y1 = randint((0 + EDGE_ZONE_SIZE), (CANVAS_HEIGHT - EDGE_ZONE_SIZE))
        x2, y2 = x1+RECTANGLE_SIDE_SIZE, y1+RECTANGLE_SIDE_SIZE

        new_rectangle = SnappableRectangle(self.canvas, x1, y1, x2, y2, "green", self)
        self.delete_buttons[new_rectangle.rect] = new_rectangle.delete_button
        
        self.rectangles.append(new_rectangle)
        self.canvas.create_window((x1, y1), window=new_rectangle.delete_button, anchor=CENTER)

        #TODO: priradit k rectanglu konkretni soubor i s ikonkou
        '''
        try:
            new_rectangle.associated_file = filedialog.askopenfilename()
        except:
            new_rectangle.delete_rectangle()
        '''

    def move_delete_button(self, delete_buttons, rect, x, y):
        if rect in delete_buttons:
            delete_button = delete_buttons[rect]
            bbox = self.canvas.bbox(rect)
            self.canvas.create_window((bbox[0] + x, bbox[1] + y), window=delete_button, anchor=NE)
    
def tkinter_extended_start():
    root = Tk_extended()
    root.title("Cog Control")

    root.canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    root.canvas.pack()

    core_rectangle = SnappableRectangle(root.canvas, 100, 100, 200, 200, "blue", root)
    root.rectangles.append(core_rectangle)

    root.canvas.bind("<ButtonPress-1>", root.on_click)
    root.canvas.bind("<B1-Motion>", root.on_drag)

    spawn_button = Button(root, text="Spawn Rectangle", command=root.spawn_rectangle)
    spawn_button.pack()

    root.mainloop()

if __name__ == "__main__":
    tkinter_extended_start()