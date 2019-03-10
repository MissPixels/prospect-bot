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
        self.getAllPossibleCombinations(self.rules)
        self.log("\n* Poet intialized")
        self.log("Rules file\t{}".format(self.rulesFiles))

    def getAllPossibleCombinations(self, rules):
        silos = rules.keys()
        combinations = []
        for silo1 in silos:
            for silo2 in silos:
                if silo1 != silo2:
                    combinations.append("{},{}".format(silo1, silo2))
        random.shuffle(combinations)
        return combinations

    def storeCombinations(self, combinations):
        combinations = filter(lambda c: c != "", combinations)
        file = open("combinations.txt", "w+")
        for combination in combinations:
            file.write("{};".format(combination))
        file.close()
        pass

    def pickOneCombination(self):
        try:
            file = open("combinations.txt", "r")
            contents = file.read()
            combinations = contents.split(";")
            combinations = list(filter(lambda c: c != "", combinations))
            if len(combinations) == 0:
                combinations = self.getAllPossibleCombinations(self.rules)
        except Exception as e:
            combinations = self.getAllPossibleCombinations(self.rules)
        index = random.randrange(len(combinations)) - 1
        combination = combinations.pop(index)
        self.storeCombinations(combinations)

        return combination

    def makePoem(self):
        grammar = tracery.Grammar(self.rules)
        grammar.add_modifiers(base_english)
        combination = self.pickOneCombination()
        combination = combination.split(",")
        origin = "#{}#\n#{}#".format(*combination)
        return grammar.flatten(origin)
