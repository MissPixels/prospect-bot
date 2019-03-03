import tracery
from tracery.modifiers import base_english
import json
import random

from app.Base import Base


class Poet(Base):
    def __init__(self):
        super(Poet, self).__init__()
        config = self.getConfig()
        self.rulesFiles = config["Poet"]["PoetRulesFile"]
        blob = open(self.rulesFiles).read()
        self.rules = json.loads(blob)
        self.log("\n* Poet intialized")
        self.log("Rules file\t{}".format(self.rulesFiles))

    def makePoem(self):
        grammar = tracery.Grammar(self.rules)
        grammar.add_modifiers(base_english)
        # Build origin
        keys = [*self.rules.keys()]
        random.shuffle(keys)
        keys = keys[:2]
        origin = "#{}#\n#{}#".format(*keys)
        return grammar.flatten(origin)
