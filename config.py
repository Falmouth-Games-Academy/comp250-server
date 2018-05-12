import sys
import json


class ConfigRolling:
    def __init__(self):
        self.database_name = "comp250"
        self.tournament_dir_path = "../tournament"
        self.enable_webhook = True
        self.enable_git = True
        self.maps = [
            "maps/10x10/basesWorkers10x10.xml",
            "maps/12x12/basesWorkers12x12.xml",
            "maps/16x16/basesWorkers16x16.xml",
            "maps/24x24/basesWorkers24x24.xml",
            "maps/8x8/bases8x8.xml",
            "maps/8x8/basesWorkers8x8Obstacle.xml",
            "maps/8x8/basesWorkers8x8.xml",
            "maps/NoWhereToRun9x8.xml"
        ]


class ConfigGrading(ConfigRolling):
    def __init__(self):
        super().__init__()
        self.database_name = "comp250_grading"
        self.tournament_dir_path = "../tournament_grading"
        self.enable_webhook = False
        self.enable_git = False
        

#config = ConfigRolling()
config = ConfigGrading()
