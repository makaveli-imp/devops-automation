import json
from argparse import Namespace
from json import JSONEncoder


class O():
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Config:
    instance = None

    def __init__(self):
        pass

    def save(self):
        self.__class__ = Config
        with open("config.json", "w") as file:
            file.write(json.dumps(self, default=lambda o: o.__dict__,
                                  sort_keys=True, indent=4))

    @staticmethod
    def load():
        import os
        if not os.path.exists("config.json"):
            Config.instance = Config()
            Config.instance.save()
        else:
            with open('config.json') as f:
                Config.instance = json.loads(f.read(), object_hook=lambda d: Namespace(**d))
        return Config.instance
