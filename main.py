import tkinter as tk

from src.ui.home import HomeApp

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeApp(root)
    root.mainloop()
