# This program can update our NBA database. Interface is the console. A user
#  may choose to:
#    1. Add a new season to our database
#    2. Copy/paste the file/folder path that they want to be
#       updated.
#  A valid file/folder path should contain all the necessary information
#  to update the necessary files.
import csv
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import shutil  # For deleting non-empty directories
import Schedule
import Team
import Player
import os
import Global


# Returns a JSON containing all data parsed from our path. The database has a
#  specific structure & depth. We can know where we are in the database based
#  on the depth of the path & keywords used with certain files.
def parsePath(pathStr):
    data = {
        "databaseLocation": "",
        "season": {
            "start": "",
            "end": ""
        },
        "team": "",
        "player": "",
        "item": {
            "isFile": True,
            "filename": ""
        }
    }

    data['item']['isFile'] = os.path.isfile(pathStr)

    path = pathStr.replace(f"{Global.BASE_PATH}/", "").split("/")
    print(path)
    depth = len(path)

    if data['item']['isFile']:
        data['item']['filename'] = os.path.basename(pathStr)
        depth -= 1  # Counts folder depth (remove file from depth count)

    season = path[0].lower().replace(" season", "").split("-")
    data['season']['start'] = season[0]
    data['season']['end'] = season[1]

    match depth:
        case 1:
            data['databaseLocation'] = "season"

        case 2:
            data['databaseLocation'] = "team"
            data['team'] = path[1]

        case 3:
            data['databaseLocation'] = "player"
            data['team'] = path[1]
            data['player'] = path[2]

    return data


# Function can do 2 types of updates based on the path received:
#   1. Directory - Update entire root folder
#   2. File - Update individual file (except log file)
# The goal of this function is to parse the path and assign the workload
#  to the proper functions within this program. Assumes default folder
#  files exist.
def update(path):
    if path.lower().find("log") != -1:
        print("Can't manually update a log file.")
        return None

    # 1. Parse data from path
    data = parsePath(path)
    databaseLocation = data['databaseLocation']
    seasonStart = data['season']['start']
    seasonEnd = data['season']['end']
    team = data['team']
    player = data['player']
    pathIsFile = data['item']['isFile']
    fileName = data['item']['filename']

    # 2. Assign Responsibilities
    match databaseLocation:
        case "season":
            print()

        case "team":
            print()

        case "player":
            # 1. Check to see if player wasn't cut/transferred to a diff. team
            cut, roster = Team.playerCut(player, team, seasonEnd)
            cut = False      # temp
            roster = []      # temp

            # 2a. Player was cut -> Notify user -> Delete existing folder ->
            #     Try to find player
            if cut:
                print(f">> {player} was cut from {team} <<")
                print(tabulate(roster))
                print(f">> {player} was cut from {team} <<")
                selection = input(
                    f"Remove player data from '{seasonStart}-{seasonEnd} Season'?  (y/n)").lower()
                while selection not in ["y", "n", "yes", "no"]:
                    print("Input not valid. Please type 'y' or 'n'.")
                    selection = input(
                        f"Remove player data from '{seasonStart}-{seasonEnd} Season'?  (y/n)").lower()

                if selection == "y" or selection == "yes":
                    removeItem(path.replace(fileName, "") if pathIsFile else path)
                    # TODO: Try to find player in their new team

            # 2b. Player not cut -> Send updates to functions
            else:
                if pathIsFile:
                    Player.updateFile(fileName, path)

                else:
                    for file in os.listdir(path):
                        if file.find("log information") != -1:
                            Player.updateFile(file, path)

    return None


# Creates a new "20XX-20XX Season" folder with all it's default files &
#  directories. ASSUMES a season folder name DNE yet.
#  Returns Nothing.
def createSeasonFolder(seasonStartYr, seasonEndYr):
    if seasonEndYr - seasonStartYr != 1:
        print(">> Season date invalid <<  Aborted season creation ")
        return None

    # Make Season Folder
    newSeasonPath = Global.BASE_PATH + f"/{seasonStartYr}-{seasonEndYr} Season"
    os.mkdir(newSeasonPath)

    # Game Schedule
    gameSchedule = Schedule.getSchedule(seasonEndYr)
    Schedule.updateSchedule(gameSchedule, seasonEndYr)

    # Make Teams Folders & populate each with player folders
    for team in getTeams():
        printTeamName(team)
        Team.initializeTeamFolder(f"{newSeasonPath}/{team}")
        print("[X] Created 3 Team Default Files.")

        rosterData = Team.getUpdatedRoster(team, seasonEndYr)
        headers = rosterData[0]
        roster = rosterData[1:]
        print(f"[X] Creating {len(roster)} player sub-folders:")
        for player in roster:
            playerName = player[0]
            Player.initializePlayerFolders(f"{newSeasonPath}/{team}/{playerName}", [headers, player])
            print(f"    [X] {playerName}")
    return None


# Gets the pre-set list of teams
def getTeams():
    teams = []
    with open(Global.BASE_PATH + "/Database Updater/Misc Files/teams list.csv", encoding='utf-8') as csvFile:
        csvReader = csv.reader(csvFile)
        for line in csvReader:
            teams.append(line[0])
    teams.pop(0)  # Pop the CSV header
    return teams


# Updates the log file. Log file contains admin data that keeps track
#  of File Name, Date, and Time of last update. Log files exist in
#  Team folders & Player folders.
def updateLogFile(fileUpdated, folderPath):
    logData = [["File", "Date Last Updated", "Time Last Updated"]]
    updated = False
    with open(f"{folderPath}/log information.csv", "r",
              encoding="utf-8") as csvFile:
        csvReader = csv.reader(csvFile)
        try:
            csvFile.readline()  # Skip Headers (if lines exist)
        except:
            pass
        for line in csvReader:
            if line[0] == fileUpdated:
                updated = True
                date, time = getDateTime()
                logData.append([fileUpdated, date, time])
            else:
                logData.append(line)

    if not updated:  # If file DNE when opened, it'll never update. So Update.
        date, time = getDateTime()
        logData.append([fileUpdated, date, time])

    with open(f"{folderPath}/log information.csv", "w", encoding="utf-8",
              newline='') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerows(logData)

    return None


# Gets the local date and time. Function called by updateLogFile().
def getDateTime():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    return date, time


# Returns the list of folders found in a path
def getFolderPaths(path):
    folders = []
    for file in os.listdir(path):
        if file.find(".") == -1:
            folders.append(path + f"/{file}")
    return folders


# Responsible for handling deletion of items. Assumes file/dir exists.
def removeItem(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)
    return None


def printTeamName(team):
    width = len(team)
    offset = 8  # Offset of characters before/after the team name

    i = 0
    while i < width + offset:
        print("#", end='')
        i += 1
    print()
    print(f"#   {team}   #")  # offset 3 on each side of logo
    i = 0
    while i < width + offset:
        print("#", end='')
        i += 1
    print()


if __name__ == "__main__":
    createSeasonFolder(seasonStartYr=2023, seasonEndYr=2024)
