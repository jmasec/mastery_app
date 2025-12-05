# container that shows mastery
# from mastery_app.lib.milestone import Milestone 
import uuid

class MasteryContainer:

    NOVICE = 20.0
    ADAVANCED_BEGINNER = 100.0
    COMPETENT = 1000.0
    PROFICIENT = 4000.0
    EXPERT = 8000.0
    MASTERY = 10000.0

    # define levels

    def __init__(self, name, cont_uuid = uuid.uuid4(), xp_level = 0.0, level = "New"):
        self.uuid = cont_uuid
        #self.milestone = Milestone()
        self.xp_level = xp_level
        self.level = level
        self.container_name = name

    def update_name(self, name):
        self.container_name = name

    def update_xp_level(self, time: float):
        self.xp_level += time
        self.level = self._check_expert_level()

    def _check_expert_level(self):
        match self.xp_level:
            case xp if xp <= self.NOVICE:
                return "New"
            case xp if xp < self.ADAVANCED_BEGINNER and xp >= self.NOVICE:
                return "Novice"
            case xp if xp < self.COMPETENT and xp >= self.ADAVANCED_BEGINNER:
                return "Advanced Beginner"
            case xp if xp < self.PROFICIENT and xp >= self.COMPETENT:
                return "Competent"
            case xp if xp < self.EXPERT and xp >= self.PROFICIENT:
                return "Proficient"
            case xp if xp < self.MASTERY and xp >= self.EXPERT:
                return "Expert"
            case _:
                return "Mastery"
            
def make_new_container(name):
    new_container = MasteryContainer(name=name)
    return new_container

def make_db_container(name, cont_uuid, xp_level, level):
    db_container = MasteryContainer(name=name, cont_uuid=cont_uuid, xp_level=xp_level, level=level)
    return db_container