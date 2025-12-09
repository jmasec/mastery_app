from mastery_app.src.display import App, User, MasteryContainer, MasteryDB, make_user_from_db, make_new_user
import tkinter as tk
from pathlib import Path

if __name__ == "__main__":

    SCRIPT_DIR = Path(__file__).resolve().parent
    DB_PATH = SCRIPT_DIR / ".." / "db" / "my_database.db"
    db = MasteryDB(DB_PATH)


    db_data = db.setup_mastery_db()
    # call func to build out user
    if db_data:
        user_rows, container_rows = db_data
        user = make_user_from_db(user_rows, container_rows, db)
    else:
        user = make_new_user("Default Name", db)

    root = tk.Tk()
    w, h = 900, 700
    root.geometry(f"{w}x{h}")

    root.update_idletasks()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.minsize(800, 600)
    App(root, db, user)
    root.mainloop()
