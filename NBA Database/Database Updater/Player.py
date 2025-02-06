# This program is responsible for updating all files regarding an *individual*
# player. Files include:
#   1. Player Characteristics
#   2. Player Season Projections
#   3. Player Totals
#   4. Player 36-Min Stats
#   5. Player Advanced Stats
import csv
import os.path
import requests
from bs4 import BeautifulSoup
import Update_Database
import Request_Ticker
import Team
from tabulate import tabulate


# Creates a player directory with EMPTY default files. Also populates the
#  "player characteristics.csv" file without calling updateCharacteristics().
def initializePlayerFolders(path, characteristicsData):
    os.makedirs(path)

    defaultPlayerFiles = ["log information.csv",
                          "player characteristics.csv",
                          "player season projections.csv",
                          "player totals.csv",
                          "player 36-Min stats.csv",
                          "player advanced stats.csv"]

    # Create log file to keep track of all other file data
    with open(f"{path}/{defaultPlayerFiles[0]}", "w", encoding='utf-8'):
        pass

    for file in defaultPlayerFiles[1:]:
        if file == defaultPlayerFiles[1]:
            with open(f"{path}/{file}", "w", encoding='utf-8', newline='') as csvFile:
                csvWriter = csv.writer(csvFile)
                csvWriter.writerows(characteristicsData)
        else:
            with open(f"{path}/{file}", "w", encoding='utf-8', newline=''):
                pass
        Update_Database.updateLogFile(fileUpdated=file, folderPath=path)

    return None


# Receives a filename (as well as a path to said file) that is guaranteed
#  to be within a player folder. It assigns the workload to the correct
#  function based on keywords in the filename. This function is called from
#  "Update_Database.py".
def updateFile(fileName, path):
    logPath = path.replace(fileName, "log information.csv")

    soup = getPlayerWebsite(logPath)
    data = []

    if fileName.find("characteristics") != -1:
        data = updateCharacteristics(logPath=logPath)
    elif fileName.find("season projection") != -1:
        # Season projections no longer supported by Basketball-Reference
        pass
    elif fileName.find("totals") != -1:
        data = updateTotals(soup=soup)
    elif fileName.find("36-min stats") != -1:
        data = update36MinStats(soup=soup)
    elif fileName.find("advanced") != -1:
        data = updateAdvancedStats(soup=soup)

    writeData(filepath=path, data=data)

    Update_Database.updateLogFile(fileUpdated=fileName, folderPath=path)


def updateCharacteristics(logPath):
    path = logPath.split("/")
    player = path[len(path)-2]
    team = path[len(path)-3]
    season = path[len(path)-4]
    seasonEndYr = season.split("-")[1].replace(" Season", "")

    data = [["Player", "Team", "Position", "Height", "Weight", "DOB", "Nationality", "Experience (Yrs)", "Website"]]
    for playerData in Team.getUpdatedRoster(team=team, seasonEndYr=seasonEndYr):
        if playerData[0] == player:
            data.append(playerData)
            return data
    print(f"\n>> {player} Cut From {team} ({season}) <<\n")
    return data


#
# OUTDATED: Basketball-Reference no longer supports this data.
#
# def updateSeasonProjections(soup):
#     projectionTable = soup.find("div", id='div_projection')
#     tableData = projectionTable.find('tbody').find('tr')
#
#     data = [["age", "fg_per_36Min", "fg_att_per_36Min",
#             "pt3_per_36Min", "pt3_att_per_36Min", "ft_per_36Min",
#             "ft_att_per_36Min", "off_rb_per_36Min", "total_rb_per_36Min",
#             "ass_per_36Min", "steals_per_36Min", "blocks_per_36Min",
#             "turn_overs_per_36Min", "perFouls_per_36Min", "pts_per_36Min",
#             "fg_pct", "pt3_pct", "ft_pct", "ws_per_48Min"]]
#     age = tableData.find('td', {'data-stat': 'age'}).text
#     fg_per_36Min = tableData.find('td', {'data-stat': 'fg_per_mp'}).text
#     fg_att_per_36Min = tableData.find('td', {'data-stat': 'fga_per_mp'}).text
#     pt3_per_36Min = tableData.find('td', {'data-stat': 'fg3_per_mp'}).text
#     pt3_att_per_36Min = tableData.find('td', {'data-stat': 'fg3a_per_mp'}).text
#     ft_per_36Min = tableData.find('td', {'data-stat': 'ft_per_mp'}).text
#     ft_att_per_36Min = tableData.find('td', {'data-stat': 'fta_per_mp'}).text
#     off_rb_per_36Min = tableData.find('td', {'data-stat': 'orb_per_mp'}).text
#     total_rb_per_36Min = tableData.find('td', {'data-stat': 'trb_per_mp'}).text
#     asst_per_36Min = tableData.find('td', {'data-stat': 'ast_per_mp'}).text
#     steals_per_36Min = tableData.find('td', {'data-stat': 'stl_per_mp'}).text
#     blocks_per_36Min = tableData.find('td', {'data-stat': 'blk_per_mp'}).text
#     turn_overs_per_36Min = tableData.find('td', {'data-stat': 'tov_per_mp'}).text
#     perFouls_per_36Min = tableData.find('td', {'data-stat': 'pf_per_mp'}).text
#     pts_per_36Min = tableData.find('td', {'data-stat': 'pts_per_mp'}).text
#     fg_pct = tableData.find('td', {'data-stat': 'fg_pct'}).text
#     pt3_pct = tableData.find('td', {'data-stat': 'fg3_pct'}).text
#     ft_pct = tableData.find('td', {'data-stat': 'ft_pct'}).text
#     ws_per_48Min = tableData.find('td', {'data-stat': 'ws_per_48'}).text
#     data.append([age, fg_per_36Min, fg_att_per_36Min,
#                  pt3_per_36Min, pt3_att_per_36Min, ft_per_36Min,
#                  ft_att_per_36Min, off_rb_per_36Min, total_rb_per_36Min,
#                  asst_per_36Min, steals_per_36Min, blocks_per_36Min,
#                  turn_overs_per_36Min, perFouls_per_36Min, pts_per_36Min,
#                  fg_pct, pt3_pct, ft_pct, ws_per_48Min])
#
#     return data


def updateTotals(soup):
    data = [["season", "age", "team",
             "position", "games", "games started",
             "minutes played", "field goals", "field goal att",
             "field goal pct", "3-Pts", "3-Pts Att",
             "3-Pts Pct", "2-Pts", "2-Pts Att",
             "2-Pts Pct", "EFG pct", "free throws",
             "free throw att", "free throw pct", "offensive rebounds",
             "defensive rebounds", "total rebounds", "assists",
             "steals", "blocks", "turnovers",
             "personal fouls", "total pts"]]
    totalsTable = soup.find("table", id="totals_stats").find('tbody')
    print(totalsTable.prettify())
    for season in totalsTable.find_all('tr'):
        try:
            seasonYrs = season.find('th', {"data-stat": "year_id"}).text.replace("-", "-20") + " Season"
            age = season.find('td', {"data-stat": "age"}).text
            team = season.find('td', {"data-stat": "team_name_abbr"}).text
            pos = season.find('td', {"data-stat": "pos"}).text
            games = season.find('td', {"data-stat": "games"}).text
            gamesStarted = season.find('td', {"data-stat": "games_started"}).text
            minPlayed = season.find('td', {"data-stat": "mp"}).text
            fieldGoals = season.find('td', {"data-stat": "fg"}).text
            fieldGoal_Att = season.find('td', {"data-stat": "fga"}).text
            fieldGoal_Pct = season.find('td', {"data-stat": "fg_pct"}).text
            pt3 = season.find('td', {"data-stat": "fg3"}).text
            pt3_Att = season.find('td', {"data-stat": "fg3a"}).text
            pt3_Pct = season.find('td', {"data-stat": "fg3_pct"}).text
            pt2 = season.find('td', {"data-stat": "fg2"}).text
            pt2_Att = season.find('td', {"data-stat": "fg2a"}).text
            pt2_Pct = season.find('td', {"data-stat": "fg2_pct"}).text
            efg_Pct = season.find('td', {"data-stat": "efg_pct"}).text
            ft = season.find('td', {"data-stat": "ft"}).text
            ft_Att = season.find('td', {"data-stat": "fta"}).text
            ft_Pct = season.find('td', {"data-stat": "ft_pct"}).text
            off_rb = season.find('td', {"data-stat": "orb"}).text
            def_rb = season.find('td', {"data-stat": "drb"}).text
            total_rb = season.find('td', {"data-stat": "trb"}).text
            ast = season.find('td', {"data-stat": "ast"}).text
            steals = season.find('td', {"data-stat": "stl"}).text
            blocks = season.find('td', {"data-stat": "blk"}).text
            turnovers = season.find('td', {"data-stat": "tov"}).text
            perFouls = season.find('td', {"data-stat": "pf"}).text
            totalPts = season.find('td', {"data-stat": "pts"}).text

            data.append([seasonYrs, age, team, pos, games, gamesStarted,
                         minPlayed, fieldGoals, fieldGoal_Att, fieldGoal_Pct,
                         pt3, pt3_Att, pt3_Pct, pt2, pt2_Att, pt2_Pct, efg_Pct,
                         ft, ft_Att, ft_Pct, off_rb, def_rb, total_rb, ast,
                         steals, blocks, turnovers, perFouls, totalPts])
        except AttributeError:
            continue
    return data


def update36MinStats(soup):
    table36MinStats = soup.find('table', id='per_minute_stats')

    data = [["season", "age", "team",
             "position", "games", "games started",
             "minutes played", "field goals", "field goal att",
             "field goal pct", "3-Pts", "3-Pts Att",
             "3-Pts Pct", "2-Pts", "2-Pts Att",
             "2-Pts Pct", "free throws", "free throw att",
             "free throw pct", "offensive rebounds", "defensive rebounds",
             "total rebounds", "assists", "steals",
             "blocks", "turnovers", "personal fouls",
             "total pts"]]
    for season in table36MinStats.find_all("tr"):
        try:
            seasonYrs = season.find('th', {"data-stat": "year_id"}).text.replace("-", "-20") + " Season"
            age = season.find('td', {"data-stat": "age"}).text
            team = season.find('td', {"data-stat": "team_name_abbr"}).text
            pos = season.find('td', {"data-stat": "pos"}).text
            games = season.find('td', {"data-stat": "games"}).text
            gamesStarted = season.find('td', {"data-stat": "games_started"}).text
            minPlayed = season.find('td', {"data-stat": "mp"}).text
            fieldGoals = season.find('td', {"data-stat": "fg_per_minute_36"}).text
            fieldGoal_Att = season.find('td', {"data-stat": "fga_per_minute_36"}).text
            fieldGoal_Pct = season.find('td', {"data-stat": "fg_pct"}).text
            pt3 = season.find('td', {"data-stat": "fg3_per_minute_36"}).text
            pt3_Att = season.find('td', {"data-stat": "fg3a_per_minute_36"}).text
            pt3_Pct = season.find('td', {"data-stat": "fg3_pct"}).text
            pt2 = season.find('td', {"data-stat": "fg2_per_minute_36"}).text
            pt2_Att = season.find('td', {"data-stat": "fg2a_per_minute_36"}).text
            pt2_Pct = season.find('td', {"data-stat": "fg2_pct"}).text
            efg_pct = season.find('td', {"data-stat": "efg_pct"}).text
            ft = season.find('td', {"data-stat": "ft_per_minute_36"}).text
            ft_Att = season.find('td', {"data-stat": "fta_per_minute_36"}).text
            ft_Pct = season.find('td', {"data-stat": "ft_pct"}).text
            off_rb = season.find('td', {"data-stat": "orb_per_minute_36"}).text
            def_rb = season.find('td', {"data-stat": "drb_per_minute_36"}).text
            total_rb = season.find('td', {"data-stat": "trb_per_minute_36"}).text
            ast = season.find('td', {"data-stat": "ast_per_minute_36"}).text
            steals = season.find('td', {"data-stat": "stl_per_minute_36"}).text
            blocks = season.find('td', {"data-stat": "blk_per_minute_36"}).text
            turnovers = season.find('td', {"data-stat": "tov_per_minute_36"}).text
            perFouls = season.find('td', {"data-stat": "pf_per_minute_36"}).text
            totalPts = season.find('td', {"data-stat": "pts_per_minute_36"}).text

            data.append([seasonYrs, age, team, pos, games, gamesStarted,
                         minPlayed, fieldGoals, fieldGoal_Att, fieldGoal_Pct,
                         pt3, pt3_Att, pt3_Pct, pt2, pt2_Att, pt2_Pct, efg_pct,
                         ft, ft_Att, ft_Pct, off_rb, def_rb, total_rb, ast,
                         steals, blocks, turnovers, perFouls, totalPts])
        except AttributeError:
            continue
    return data


def updateAdvancedStats(soup):
    advancedTable = soup.find('table', id='advanced').find('tbody')

    data = [["season", "age", "team",
             "league", "position", "total games",
             "games started", "minutes played", "player efficiency rating",
             "true shooting pct", "3-Pts att rate", "free throw att rate",
             "offensive rebound rate", "defensive rebound rate", "total rebound rate",
             "assist pct", "steal pct", "block pct",
             "turnover pct", "player usage pct", "offensive win shares",
             "defensive win shares", "win shares", "win shares (per 48 min)",
             "offensive box plus minus", "defensive box plus minus", "box plus minus",
             "value over replacement player"]]
    for season in advancedTable.find_all('tr'):
        try:  # Ignores missing years
            seasonYrs = season.find('th', {"data-stat": "year_id"}).text.replace("-", "-20") + " Season"
            age = season.find('td', {"data-stat": "age"}).text
            team = season.find('td', {"data-stat": "team_name_abbr"}).text
            league = season.find('td', {"data-stat": "comp_name_abbr"}).text
            pos = season.find('td', {"data-stat": "pos"}).text
            totalGames = season.find('td', {"data-stat": "games"}).text
            gamesStarted = season.find('td', {"data-stat": "games_started"}).text
            minPlayed = season.find('td', {"data-stat": "mp"}).text
            playerEffRating = season.find('td', {"data-stat": "per"}).text
            trueShootingPct = season.find('td', {"data-stat": "ts_pct"}).text
            pt3_att_rate = season.find('td', {"data-stat": "fg3a_per_fga_pct"}).text
            freeThrow_att_rate = season.find('td', {"data-stat": "fta_per_fga_pct"}).text
            off_rebound_pct = season.find('td', {"data-stat": "orb_pct"}).text
            def_rebound_pct = season.find('td', {"data-stat": "drb_pct"}).text
            total_rebound_pct = season.find('td', {"data-stat": "trb_pct"}).text
            ast_pct = season.find('td', {"data-stat": "ast_pct"}).text
            steal_pct = season.find('td', {"data-stat": "stl_pct"}).text
            block_pct = season.find('td', {"data-stat": "blk_pct"}).text
            turnover_pct = season.find('td', {"data-stat": "tov_pct"}).text
            player_usage_pct = season.find('td', {"data-stat": "usg_pct"}).text
            off_win_shares = season.find('td', {"data-stat": "ows"}).text
            def_win_shares = season.find('td', {"data-stat": "dws"}).text
            win_shares = season.find('td', {"data-stat": "ws"}).text
            win_shares_per_48Min = season.find('td', {"data-stat": "ws_per_48"}).text
            off_box_plusMinus = season.find('td', {"data-stat": "obpm"}).text
            def_box_plusMinus = season.find('td', {"data-stat": "dbpm"}).text
            box_plusMinus = season.find('td', {"data-stat": "bpm"}).text
            vorp = season.find('td', {"data-stat": "vorp"}).text

            data.append([seasonYrs, age, team, league, pos, totalGames,
                         gamesStarted, minPlayed, playerEffRating,
                         trueShootingPct, pt3_att_rate, freeThrow_att_rate,
                         off_rebound_pct, def_rebound_pct, total_rebound_pct,
                         ast_pct, steal_pct, block_pct, turnover_pct,
                         player_usage_pct, off_win_shares, def_win_shares,
                         win_shares, win_shares_per_48Min, off_box_plusMinus,
                         def_box_plusMinus, box_plusMinus, vorp])
        except AttributeError:
            continue

    return data


# Writes data to a CSV file. Returns nothing.
def writeData(filepath, data):
    with open(filepath, "w", encoding='utf-8', newline='') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerows(data)

    Update_Database.updateLogFile(fileUpdated=os.path.basename(filepath),
                                  folderPath=os.path.dirname(filepath))
    return None


def getPlayerWebsite(logfilePath):
    data = []
    logfilePath = logfilePath.replace('log information.csv', 'player characteristics.csv')
    with open(logfilePath, "r") as csvFile:
        csvReader = csv.reader(csvFile)  # Skip Headers
        for line in csvReader:
            data.append(line)
    url = data[1][8]

    Request_Ticker.addRequest()
    website = requests.get(url).content
    return BeautifulSoup(website, "html.parser")


# This function converts our Soup obj to a String. Replaces the commented
#  out HTML "<!-- -->" with "". Then, converts the string back to a Soup
#  obj so we can extract the necessary data. Necessary since BeautifulSoup
#  can't read commented out HTML. Function not currently in use. But useful
#  when site is undergoing updates.
def extractCommentedHTML(soup):
    myStr = str(soup)
    myStr = myStr.replace("<!--", "")
    myStr = myStr.replace("-->", "")

    return BeautifulSoup(myStr, 'html.parser')


if __name__ == "__main__":
    teamPath = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database/2024-2025 Season/Atlanta Hawks"
    roster = [d for d in os.listdir(teamPath) if os.path.isdir(os.path.join(teamPath, d))]
    for player in roster:
        print(f"[X] Updating {player} Folder")
        logfilePath = f"{teamPath}/{player}/log information.csv"

        # Updating this first to update player website (req. for soup)
        # data = updateCharacteristics(logfilePath)
        # writeData(filepath=logfilePath.replace('log information.csv',
        #                                        'player characteristics.csv'),
        #           data=data)
        # print(f"\t[X] updateCharacteristics()")

        soup = getPlayerWebsite(logfilePath)

        # data = updateAdvancedStats(soup)
        # writeData(filepath=logfilePath.replace('log information.csv',
        #                                        'player advanced stats.csv'),
        #           data=data)
        # print(f"\t[X] updateAdvancedStats()")
        # print(tabulate(data))

        # data = updateTotals(soup)
        # writeData(filepath=logfilePath.replace('log information.csv',
        #                                        'player totals.csv'),
        #           data=data)
        # print(f"\t[X] updateTotals()")
        # print(tabulate(data))

        # data = update36MinStats(soup)
        # writeData(filepath=logfilePath.replace('log information.csv',
        #                                        'player 36-Min stats.csv'),
        #           data=data)
        # print(f"\t[X] update36MinStats()")
        # print(tabulate(data))
