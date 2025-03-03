import tkinter as tk
from PIL import Image, ImageTk

class JarvisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis AI Assistant")
        self.root.geometry("800x600")

        # Load GIF
        self.gif = Image.open("jarvis.gif")
        self.gif_frames = []
        try:
            while True:
                self.gif_frames.append(ImageTk.PhotoImage(self.gif.copy()))
                self.gif.seek(len(self.gif_frames))  # Move to next frame
        except EOFError:
            pass

        self.current_frame = 0
        self.label = tk.Label(root)
        self.label.pack()

        self.animate()

    def animate(self):
        self.label.config(image=self.gif_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
        self.root.after(100, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()