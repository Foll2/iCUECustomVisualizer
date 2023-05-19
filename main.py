import json
import os
import time
import tkinter as tk
from PIL import Image, ImageTk

image_path = "background.png"
json_path = "settings.json"

debug = False

class DisplayApp(tk.Tk):
    def __init__(self, json_file):
        super().__init__()
        self.title("iCUE JSON Display")
        width, height = Image.open(image_path).size
        self.canvas = tk.Canvas(self, width=width, height=height)
        self.canvas.pack()
        self.blocks = {}
        self.json_file = json_file
        self.json_data = None
        self.last_modified = None
        self.selected_block = None
        self.prev_event = None
        self.load_json()
        self.load_background_image()
        self.display_json()
        self.check_json_changes()

        self.canvas.bind("<Button-1>", self.select_block)
        self.canvas.bind("<B1-Motion>", self.move_block)
        self.canvas.bind("<Button-3>", self.start_scaling_block)
        self.canvas.bind("<B3-Motion>", self.scale_block)
        self.bind("<Control-s>", self.save_json)
        self.bind("<Control-d>", self.duplicate_block)

        self.add_polygon_button = tk.Button(self, text="Add Polygon", command=self.add_polygon)
        self.add_polygon_button.pack()
        self.delete_button = tk.Button(self, text="Delete Polygon", command=self.delete_block)
        self.delete_button.pack()

    # Block/JSON Deletion
    
    def delete_block(self):
        if self.selected_block:
            block_id = self.selected_block[0]
            polygon_id = next((k for k, v in self.blocks.items() if v == block_id), None)
            if polygon_id:
                self.canvas.delete(block_id)
                self.blocks.pop(polygon_id)
                self.remove_polygon_from_json(polygon_id)
            self.selected_block = None
        else:
            print("No Block Selected")

    def remove_polygon_from_json(self, polygon_id):
        for view in self.json_data.get("Defaults", {}).get("Keyboard", {}).get("Views", []):
            polygons = view.get("Polygons", [])
            for i, polygon in enumerate(polygons):
                if polygon["Id"] == polygon_id:
                    del polygons[i]
                    print("Deleted Polygon")
                    break
    
        max_id = max(item["Id"] for view in self.json_data.get("Defaults", {}).get("Keyboard", {}).get("Views", []) for item in view.get("Polygons", []))
    
        for view in self.json_data.get("Defaults", {}).get("Keyboard", {}).get("Views", []):
            polygons = view.get("Polygons", [])
            for item in polygons:
                if item["Id"] > polygon_id:
                    item["Id"] -= 1
                    if item["Id"] > max_id:
                        max_id = item["Id"]
    
    # Add Block

    def add_polygon(self):
        print("Adding Block")
        path = "M 0 0 L 100 0 L 100 100 L 0 100 Z"
        coords = self.parse_path(path)
        block_id = self.canvas.create_polygon(coords, outline='red', fill='', tags="block")
        self.blocks[block_id] = len(self.blocks) + 1

        polygon_id = len(self.json_data['Defaults']['Keyboard']['Views'][0]['Polygons']) + 1
        new_polygon = {
            "Id": polygon_id,
            "Path": path
        }
        self.json_data["Defaults"]["Keyboard"]["Views"][0]["Polygons"].append(new_polygon)
        self.save_json(None)


    def duplicate_block(self, event):
        if self.selected_block:
            block_id = self.selected_block[0]
            coords = self.canvas.coords(block_id)
            new_block_id = self.canvas.create_polygon(coords, outline='red', fill='', tags="block")
            self.blocks[new_block_id] = len(self.blocks) + 1

            polygon_id = next((k for k, v in self.blocks.items() if v == block_id), None)
            print(polygon_id)
            if polygon_id:
                path = self.json_data["Defaults"]["Keyboard"]["Views"][0]["Polygons"][polygon_id - 1]["Path"]
                print(path)
                new_polygon = {
                    "Id": polygon_id,
                    "Path": path
                }
                self.json_data["Defaults"]["Keyboard"]["Views"][0]["Polygons"].append(new_polygon)
                self.save_json(None)
        else:
            print("No Block Selected")



    def select_block(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if "block" in self.canvas.gettags(item):
            self.selected_block = item
            #self.canvas.itemconfig(item[0], outline='white')
        else:
            self.selected_block = None

    # Transform Block

    def move_block(self, event):
        if self.selected_block:
            block_id = self.selected_block[0]
            self.canvas.move(block_id, event.x - self.canvas.coords(block_id)[0], event.y - self.canvas.coords(block_id)[1])

    def start_scaling_block(self, event):
        self.prev_event = event

    def scale_block(self, event):
        if self.selected_block and self.prev_event:
            block_id = self.selected_block[0]
            scale_x = 1 + (event.x - self.prev_event.x) / 100
            scale_y = 1 + (event.y - self.prev_event.y) / 100
            self.canvas.scale(block_id, event.x, event.y, scale_x, scale_y)
            self.prev_event = event

    # Load And Display Blocks

    def load_json(self):
        with open(self.json_file) as f:
            self.json_data = json.load(f)

    def load_background_image(self):
        self.background_photo = ImageTk.PhotoImage(file=rf"{image_path}")
        self.canvas.create_image(0, 0, image=self.background_photo, anchor=tk.NW, tags="background")

    def check_json_changes(self):
        current_modified = time.ctime(os.path.getmtime(self.json_file))
        if self.last_modified != current_modified:
            self.last_modified = current_modified
            self.load_json()
            self.display_json()

        self.after(1000, self.check_json_changes)

    def display_json(self):
        self.canvas.delete("block")
        self.blocks = {}
        keyboard_data = self.json_data.get("Defaults", {}).get("Keyboard", {})
        for view in keyboard_data.get("Views", []):
            for polygon in view.get("Polygons", []):
                path = polygon["Path"]
                coords = self.parse_path(path)
                block_id = self.canvas.create_polygon(coords, outline='red', fill='', tags="block")
                self.blocks[polygon["Id"]] = block_id
                if debug == True:
                    print(f"Coords json: {coords}")
                    print(f"Id: {block_id}")
                    print(f"Blocks json: {self.blocks}")

    # Saving Functions

    def parse_path(self, path):
        path_parts = path.split()
        coords = []
        for part in path_parts:
            if part.isnumeric():
                coords.append(int(part))
        return [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
    
    def save_json(self, event):
        if debug == True:
            print(f"Blocks: {self.blocks}")
        else:
            print("Saving")
        for polygon_id in self.blocks.values():
            coords = self.canvas.coords(polygon_id)
            path = "M " + " L ".join([f"{int(coords[i])} {int(coords[i+1])}" for i in range(0, len(coords), 2)])
            path += " Z"
            if debug == True:
                print(f"Coord: {coords}")
                print(f"Path: {path}")

            polygon_id = next((k for k, v in self.blocks.items() if v == polygon_id), None)
            if polygon_id:
                for view in self.json_data.get("Defaults", {}).get("Keyboard", {}).get("Views", []):
                    for polygon in view.get("Polygons", []):
                        if polygon["Id"] == polygon_id:
                            polygon["Path"] = path
                            break

        with open(self.json_file, "w") as f:
            json.dump(self.json_data, f, indent=4)


            
if __name__ == "__main__":
    app = DisplayApp(json_path)
    app.mainloop()
