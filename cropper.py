import os
from PIL import ImageTk, Image
from tkinter import Tk, Frame, filedialog, PhotoImage, Canvas, LEFT, Button, BOTTOM

def is_image(fn):
    exts = [".jpg", ".jpeg", ".png", ".gif"]
    return any(fn.endswith(ext) for ext in exts)

def list_files(path):
    with os.scandir(path) as entries:
        return sorted([e.name for e in entries if is_image(e.name)])

def interpolate_crop_areas(large, small, count, reps):
    steps = [(small[side] - large[side]) / (count - 1) for side in range(0, 4)]
    sides = [[large[side] + steps[side] * i for i in range(0, count)] for side in range(0, 4)]
    for i in range(0, len(sides)):
        sides[i] = sorted(sides[i] * reps)
    sides[2].reverse()
    sides[3].reverse()
    return sides

def crop_images(dir, files, large, small, count, reps):
    save_dir = dir + "/cropped"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    c = interpolate_crop_areas(large, small, count, reps)
    for i in range(0, len(files)):
        with Image.open(dir+"/"+files[i]) as image:
            area = (c[0][i], c[1][i], c[2][i], c[3][i])
            print(area)
            image = image.crop(area)
            root, ext = os.path.splitext(save_dir + "/" + files[i])
            image.save(root + "_cropped.jpg")
            print(str(i+1) + " of " + str(len(files)) + " done")

class CropperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sequence Image Cropper")
        self.master.configure(background="gray20")
        self.corners = [[],[]]
        self.images = []
        self.orig_dims = []
        self.thmb_dims = []
        self.button = Button(master, text="CROP", command=self.on_submit)
        self.button.configure(highlightbackground="gray20", width=30, height=2)
        self.button.pack(side=BOTTOM)
        self.setup_canvases()
        self.setup_images()

    def setup_canvases(self):
        self.canvases = []
        self.canvases.append(Canvas(self.master, width=500, height=500))
        self.canvases[0].bind("<Button-1>",
            lambda event, id="c1": self.on_click(event, id))
        self.canvases[0].configure(background="gray20")
        self.canvases[0].pack(side=LEFT)
        self.canvases.append(Canvas(self.master, width=500, height=500))
        self.canvases[1].bind("<Button-1>",
            lambda event, id="c2": self.on_click(event, id))
        self.canvases[1].configure(background="gray20")
        self.canvases[1].pack(side=LEFT)

    def setup_images(self):
        self.master.update()
        self.dirname = filedialog.askdirectory(initialdir = "~")
        self.files = list_files(self.dirname)
        self.images.append(
            self.get_photoimage(self.dirname+"/"+self.files[0]))
        self.images.append(
            self.get_photoimage(self.dirname+"/"+self.files[-1]))
        self.reset_images()

    def get_photoimage(self, path):
        image = Image.open(path)
        self.orig_dims.append(image.size)
        image.thumbnail([500, 500], Image.ANTIALIAS)
        self.thmb_dims.append(image.size)
        return ImageTk.PhotoImage(image)

    def reset_image(self, image_idx):
        self.canvases[image_idx].create_image(
            0, 0, image=self.images[image_idx], anchor="nw")

    def reset_images(self):
        self.reset_image(0)
        self.reset_image(1)

    def on_click(self, event, id):
        if id == "c1":
            self.handle_new_corners([event.x, event.y],
                self.corners[0], self.canvases[0], 0)
        if id == "c2":
            self.handle_new_corners([event.x, event.y],
                self.corners[1], self.canvases[1], 1)

    def on_submit(self):
        if len(self.corners[0]) == 2 and len(self.corners[1]) == 2:
            print("Cropping images...")
            self.corners[0][0] = self.thmb_pos_to_orig_pos(self.corners[0][0],0)
            self.corners[0][1] = self.thmb_pos_to_orig_pos(self.corners[0][1],0)
            self.corners[1][0] = self.thmb_pos_to_orig_pos(self.corners[1][0],1)
            self.corners[1][1] = self.thmb_pos_to_orig_pos(self.corners[1][1],1)
            print("Corners: " + str(self.corners))
            crop_large = [self.corners[0][0][0], self.corners[0][0][1],
                self.corners[0][1][0], self.corners[0][1][1]]
            crop_small = [self.corners[1][0][0], self.corners[1][0][1],
                self.corners[1][1][0], self.corners[1][1][1]]
            # TODO: add inputs for count and repetitions
            crop_images(self.dirname, self.files, crop_large, crop_small, 12, 5)

    def handle_new_corners(self, corner, corners, canvas, image_idx):
        if len(corners) == 2:
            corners.clear()
        corners.append(corner)
        if len(corners) == 1:
            self.reset_image(image_idx)
        if len(corners) == 2:
            canvas.create_rectangle(
                corners[0][0], corners[0][1], corners[1][0], corners[1][1],
                outline="magenta", width=2)

    def thmb_pos_to_orig_pos(self, pos, image_idx):
        w_ratio = self.orig_dims[image_idx][0]/self.thmb_dims[image_idx][0]
        h_ratio = self.orig_dims[image_idx][1]/self.thmb_dims[image_idx][1]
        return [pos[0] * w_ratio, pos[1] * h_ratio]

def main():
    root = Tk()
    gui = CropperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
