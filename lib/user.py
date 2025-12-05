from mastery_app.lib.mastery_container import MasteryContainer, make_new_container 
from mastery_app.lib.mastery_db import MasteryDB 
import uuid

class User:
    def __init__(self, username, user_uuid = uuid.uuid4(), containers: dict[str, MasteryContainer] = {}, db = MasteryDB("../db/test.db")):
        self.uuid = user_uuid
        self.username = username
        self.containers: dict[str, MasteryContainer] = containers
        self.db = db

    def new_container(self, name: str):
        new_container = make_new_container(name=name)
        if name in self.containers:
            print("XP Container already exists")
            return None
        self.containers[name] = new_container
        return new_container

    def delete_container(self, name):
        if name not in self.containers:
            print("XP container does not exist")
            return -1
        else:
            del self.containers[name]
            return 0

    def update_username(self, name):
        self.username = name

def make_new_user(name):
    new_user = User(username=name)
    return new_user

def make_user_from_db(user_rows, container_rows, db):
    # just support one user right now
    user = User(user_uuid=user_rows[0]["id"], username=user_rows[0]["username"], db=db)

    for cont in container_rows:
        temp_container = MasteryContainer(name=cont['name'], cont_uuid=cont['id'], xp_level=cont['xp_level'], level=cont['level'])
        user.containers[cont['name']] = temp_container
    
    return user

def add_container_db():
    pass