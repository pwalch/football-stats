# Actual match API

from enum import Enum
import json
from datetime import date

class Minute:
    def __init__(self, minuteObject):
        self.normal = minuteObject['normal']
        self.added = minuteObject['added']

    def getNormal(self):
        return self.normal

    def getAdded(self):
        return self.added

    def toString(self):
        return str(self.normal) + "'+" + str(self.added) if self.added > 0\
            else str(self.normal) + "'"

class GoalType(Enum):
    REGULAR = 1
    PENALTY = 2
    OWN_GOAL = 3

class Goal:
    def __init__(self, goalObject):
        self.scorer = goalObject['scorer']
        self.goalType = {
            "regular": GoalType.REGULAR,
            "penalty": GoalType.PENALTY,
            "own goal": GoalType.OWN_GOAL
        }[goalObject['goalType']]
        self.minute = Minute(goalObject['minute'])

    def getScorer(self):
        return self.scorer

    def getType(self):
        return self.goalType

    def getMinute(self):
        return self.minute

    def toString(self):
        goalTypeString = {
            GoalType.REGULAR: "Regular",
            GoalType.PENALTY: "Penalty",
            GoalType.OWN_GOAL: "Own goal"
        }[self.goalType]

        return self.minute.toString() + " " + self.scorer + " (" + goalTypeString + ")"

class CardColor(Enum):
    YELLOW = 1
    RED = 2

class Card:
    def __init__(self, cardObject):
        self.color = {
            "yellow": CardColor.YELLOW,
            'red': CardColor.RED,
        }[cardObject['color']]
        self.minute = Minute(cardObject['minute'])

    def getColor(self):
        return self.color

    def getMinute(self):
        return self.minute

    def toString(self):
        return self.minute.toString() + ", " + self.color

class Player:
    def __init__(self, playerObject):
        self.name = playerObject['name']
        self.number = int(playerObject['number'])

        self.cards = list()
        for cardObject in playerObject['cards']:
            self.cards.append(Card(cardObject))

    def getName(self):
        return self.name

    def getShirtNumber(self):
        return self.number

    def getCards(self):
        return self.cards

    def toString(self):
        playerDescription = str(self.number) + ". " + self.name
        nbCards = len(self.cards)
        if nbCards == 1:
            card = self.cards[0]
            if card.color == 'red':
                playerDescription += ", sent off (" + card.getMinute().toString() + ")"
            else:
                playerDescription += ", booked (" + card.getMinute().toString() + ")"

        elif nbCards == 2:
            firstCard = self.cards[0]
            secondCard = self.cards[1]

            playerDescription += ", booked (" + firstCard.getMinute().toString() +\
                                 ") then sent off (" + secondCard.getMinute().toString() + ")";

        elif nbCards == 3:
            firstCard = self.cards[0]
            secondCard = self.cards[1]
            playerDescription += ", booked (" + firstCard.getMinute().toString() +\
                                 "), booked again and sent off (" + secondCard.getMinute().toString() + ")";

        return playerDescription


class Substitution:
    def __init__(self, replacementObject):
        self.replacedName = replacementObject['name']
        self.minute = Minute(replacementObject['minute'])

    def getSubstitutedName(self):
        return self.replacedName

    def getMinute(self):
        return self.minute

class Substitute(Player):
    def __init__(self, substituteObject):
        super().__init__(substituteObject)
        self.substitution = Substitution(substituteObject['replacement'])\
            if substituteObject['replacement'] is not None else None

    def getSubstitution(self):
        return self.substitution

    def toString(self):
        playerDescription = super(Substitute, self).toString()
        if self.substitution is not None:
            playerDescription += ". Replaced " + self.substitution.replacedName +\
                             " (" + self.substitution.getMinute().toString() + ")"

        return playerDescription

class Side:
    def __init__(self, sideObject):
        self.name = sideObject['name']
        self.fullTimeGoals = int(sideObject['fulltimegoals'])

        self.shotsOnTarget = int(sideObject['shotsontarget']) if sideObject['shotsontarget'] is not None else None
        self.shotsWide = int(sideObject['shotswide']) if sideObject['shotswide'] is not None else None

        self.goalList = list()
        for goalObject in sideObject['goals']:
            self.goalList.append(Goal(goalObject))

        self.lineup = list()
        for playerObject in sideObject['lineup']:
            self.lineup.append(Player(playerObject))

        self.substitutes = list()
        for substituteObject in sideObject['substitutes']:
            self.substitutes.append(Substitute(substituteObject))

    def getName(self):
        return self.name

    def getFullTimeGoals(self):
        return self.fullTimeGoals

    def getShotsOnTarget(self):
        return self.shotsOnTarget

    def getShotsWide(self):
        return self.shotsWide

    def getGoalList(self):
        return self.goalList

    def getLineup(self):
        return self.lineup

    def getBench(self):
        return self.substitutes

    def toTeamString(self):
        teamString = "Lineup\n"
        for player in self.getLineup():
            teamString += player.toString() + "\n"

        teamString += "Bench\n"
        for player in self.getBench():
            teamString += player.toString() + "\n"

        return teamString

    def toGoalsString(self):
        goalString = ""
        if len(self.goalList) > 0:
            for goal in self.goalList:
                goalString += goal.toString() + "\n"
        else:
            goalString += "No goals\n"

        return goalString

class BaseMatch:
    def __init__(self, eventDate):
        self.eventDate = eventDate

    def getDate(self):
        return self.eventDate

    def getDateString(self):
        return "{:%d %b %Y}".format(self.eventDate)

class Match(BaseMatch):
    def __init__(self, matchPath):
        with open(matchPath, 'r', encoding='utf-8') as matchFile:
            matchObject = json.load(matchFile)

            matchDate = matchObject['date']
            super().__init__(date(matchDate['year'], matchDate['month'], matchDate['day']))

            self.sides = dict()
            self.sides['home'] = Side(matchObject['home'])
            self.sides['away'] = Side(matchObject['away'])

    def getHomeSide(self) -> Side:
        return self.sides['home']

    def getAwaySide(self) -> Side:
        return self.sides['away']

    def toShortString(self):
        return self.getDateString() + ": " +\
            self.getHomeSide().getName() + " " + str(self.getHomeSide().getFullTimeGoals()) +\
            " - " + str(self.getAwaySide().getFullTimeGoals()) + " " + self.getAwaySide().getName()

    def toString(self):
        homeShots = self.getHomeSide().getShotsWide() + self.getHomeSide().getShotsOnTarget()
        awayShots = self.getAwaySide().getShotsWide() + self.getAwaySide().getShotsOnTarget()

        return self.toShortString() + "\n" + \
            "Shots : " + str(homeShots) + " - " + str(awayShots) + "\n" + \
            "Shots on target : " + str(self.getHomeSide().getShotsOnTarget()) + " - " +\
            str(self.getAwaySide().getShotsOnTarget()) + "\n" + "\n" \
            "Home goals\n" + self.getHomeSide().toGoalsString() + "\n" \
            "Away goals\n" + self.getAwaySide().toGoalsString() + "\n" \
            "Home team\n" + self.getHomeSide().toTeamString() + "\n" \
            "Away team\n" + self.getAwaySide().toTeamString()