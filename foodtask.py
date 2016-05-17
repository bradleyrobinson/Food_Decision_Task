import random
__metaclass__ = type

class DecisionCooperate:
    def __init__(self, money):
        self.choiceList = []
        self.tempList = []
        self.currentMoney = money
        self.cc = -3.00
        self.dc = -7.00
        self.cd = -2.00
        self.dd = -6.00

    def set_payoff_matrix(self, cc, cd, dc, dd):
        self.cc = cc
        self.cd = cd
        self.dc = dc
        self.dd = dd

    def payoff(self, choice_a, choice_b):
        if choice_a == 'c' and choice_b == 'c':
            self.currentMoney += self.cc + self.cc
        elif choice_a == 'c' and choice_b == 'd':
            self.currentMoney += self.cd + self.cd
        elif choice_a == 'd' and choice_b == 'c':
            self.currentMoney += self.dc + self.cd
        elif choice_a == 'd' and choice_b == 'd':
            self.currentMoney += self.dc + self.dd

    def record_decision(self, item1, item2, preference1, preference2, choice):
        self.tempList = [item1, item2, preference1, preference2, choice]
        self.choiceList.append(self.tempList)

    def get_list(self):
        return self.choiceList



class RatedFood:
    def __init__(self):
        self.foodScores = {}

    def addFood(self, food, rating):
        self.foodScores[food] = rating

    def getRandom(self):
        return random.choice(self.foodScores.keys())

    def getList(self):
        return self.foodScores

    def getRating(self, item):
        return self.foodScores[item]


cheese = RatedFood()
cheese.addFood('cheese', 10)
