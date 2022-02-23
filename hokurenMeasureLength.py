import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)

        self.master.title("Hokuren Measure Length")
        self.master.state("zoomed")

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    app.mainloop()