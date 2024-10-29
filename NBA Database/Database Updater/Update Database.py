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
            #     Try to find player.
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


# Creates a new "20XX-20XX Season" folder. ASSUMES a duplicate folder name DNE.
#  After creation, it populates the folder with sub-folders & placeholder files.
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

    # Make Teams Folders
    createTeamsFolders(newSeasonPath)

    # TODO: Create player folders to each team folder
    for teamFolder in getFolderPaths(newSeasonPath):
        continue

    return None


# Creates a team folder for all 30 NBA teams. ASSUMES the parent folder
#  "20XX-20XX Season" is already created. "Placeholder" files are also
#  created for each team:
#    1. Team Statistics
#    2. Log information
#  Player folders are also populated with real data. Details on files
#  contained for each player folder can be found in a different function.
# TODO: Add placeholder log files when creating each team folder
# TODO: Add boolean arg, if need to populate with roster folders for each team
def createTeamsFolders(path):
    # Gets the pre-set list of teams
    teams = []
    with open(Global.BASE_PATH + "/Database Updater/Misc Files/teams list.csv", encoding='utf-8') as csvFile:
        csvReader = csv.reader(csvFile)
        for line in csvReader:
            teams.append(line[0])
    teams.pop(0)  # Pop the CSV header

    # Make folders if DNE
    for team in teams:
        try:
            os.mkdir(path + f"/{team}")
        except FileExistsError:
            continue


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


if __name__ == "__main__":
    print()
