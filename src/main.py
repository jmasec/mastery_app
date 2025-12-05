from mastery_app.src.display import App, User, MasteryContainer, MasteryDB, make_user_from_db, make_new_user
import tkinter as tk
from pathlib import Path
import uuid

if __name__ == "__main__":

    SCRIPT_DIR = Path(__file__).resolve().parent
    DB_PATH = SCRIPT_DIR / ".." / "db" / "my_database.db"
    # here we read in db first to make the User profile
    db = MasteryDB(DB_PATH)

    user_uuid = str(uuid.uuid4())
    db.insert_user_db(user_uuid, "testuser")
    db.insert_container_db("C Programming",user_uuid)
    db_data = db.setup_mastery_db()
    # call func to build out user
    if db_data:
        user_rows, container_rows = db_data
        user = make_user_from_db(user_rows, container_rows, db)
    else:
        user = make_new_user("Default Name")

    # cont = MasteryContainer(name="1", xp_level=50)
    # a = {"test": cont}
    # user = User(username="yo", containers=a)
    root = tk.Tk()
    App(root, user)
    root.mainloop()
