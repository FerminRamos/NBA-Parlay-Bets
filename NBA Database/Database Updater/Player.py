# This program is responsible for updating all files regarding an *individual*
# player. Files include:
#   1. Player Characteristics
#   2. Player Season Projections
#   3. Player Totals
#   4. Player 36-Min Stats
#   5. Player Advanced Stats
#   6. File log information
import csv
import os.path
from tabulate import tabulate
import requests
import json
from bs4 import BeautifulSoup
import Team
import Global
import Update_Database


def initializePlayerFolder(path):
    os.makedirs(path)

    defaultPlayerFiles = ["player characteristics.csv",
                          "player season projections.csv",
                          "player totals.csv",
                          "player 36-Min stats.csv",
                          "player advanced stats.csv"]
    for file in defaultPlayerFiles:
        with open(f"{path}/{file}", "w"):
            pass
        Update_Database.updateLogFile(fileUpdated=file, folderPath=path)

    return None


# Receives a filename (as well as a path to said file) that is guaranteed
#  to be within a player folder. It assigns the workload to the correct
#  function based on keywords in the filename. This function is called from
#  "Update_Database.py"
def updateFile(fileName, path):
    logPath = path.replace(fileName, "log information.csv")

    if fileName.find("characteristics") != -1:
        updateCharacteristics(logfilePath=logPath)
    elif fileName.find("season projection") != -1:
        updateSeasonProjections(logfilePath=logPath)
    elif fileName.find("totals") != -1:
        updateTotals(logfilePath=logPath)
    elif fileName.find("36-min stats") != -1:
        update36MinStats(logfilePath=logPath)
    elif fileName.find("advanced") != -1:
        updateAdvancedStats(logfilePath=logPath)

    Update_Database.updateLogFile(fileUpdated=fileName, folderPath=path)


# Updates a player's characteristics CSV file. Reads the player's log file to
#  get their website URL -> Webscrapes URL and pulls characteristics data.
#  Assumes log file is up-to-date.
#  Returns nothing, updates log file and characteristics CSV file.
def updateCharacteristics(logfilePath):
    return None


def updateSeasonProjections(logfilePath):
    return None


def updateTotals(logfilePath):
    return None


def update36MinStats(logfilePath):
    return None


def updateAdvancedStats(logfilePath):
    return None


if __name__ == "__main__":
    seasonFolder = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2023-2024 Season"
    gameSchedule = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2023-2024 Season/2023-2024 Game Schedule.csv"
    teamFolder = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2023-2024 Season/Boston Celtics"
    rosterOverview = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2023-2024 Season/Boston Celtics/roster overview.csv"
    playerFolder = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2023-2024 Season/Boston Celtics/Player 1"
    playerSeasonProj = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2023-2024 Season/Boston Celtics/Player 1/season projections.csv"
