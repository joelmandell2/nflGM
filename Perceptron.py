import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import csv
import os
import time
import json
import re
import string
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.sql.util import expand_column_list_from_order_by



#todo: pass into model and predict
#todo: create api that connects to react frontend
#todo: potentially host data on a database for frontend so the website is more customizable




#todo: train model on multiple years of data (only one position per training)
#todo: use multiclass perceptrons, as well as random forest and compare results
#todo: predict based off of model
#todo: graph results

# 1.) Train
# use round as a measure of success
# account for missing data with null values/Average value placement
# get a scale value like height 5'5-7 feet

n_count = 0


def parse_name_index(name):
    global n_count
    if n_count > 5:
        time.sleep(10)
        n_count = 0
    n_count += 1
    split_name = name.split(' ')
    base_url = 'https://www.pro-football-reference.com/players/'
    base_url2 = 'https://www.pro-football-reference.com'

    last_name = (split_name[1][0]).upper()

    name = name.title()
    new_url = base_url + last_name + '/'
    print('checking index')

    page = requests.get(new_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('a')
    for t in table:
        if name in t:
            st_url = str(t)
            split_u = st_url.split('href="')
            split_again = split_u[1].split('.htm')
            return base_url2 + split_again[0] + '/splits/'

    return new_url


def parse_nfl_stats(position, count, attr):
    # 0 year, 1 team, 2 games, 3 tackles, 4 solo, 5 ast, 6 sack, 7 safety, 8 pdef, 9 int, 10 tds, 11 yds, 12 avg, 13 lng
    if position == 'DEFENSE':
        if count == 2:
            return ('solo', attr)
        elif count == 4:
            return ('tackles', attr)
        elif count == 5:
            return ('tfl', attr)
        elif count == 6:
            return ('sack', attr)
        elif count == 7:
            return ('int', attr)
        elif count == 10:
            return ('pd', attr)
        else:
            return -1
    # 1 = comp, 2 = attempts, 3 = pct 4 = yds, 5 = td, 6= int, 7 = rate, 8 = att, 9 = yds, 10 = avg, 11 = td
    if position == 'QB':
        if count == 3:
            return ('att', attr)
        elif count == 4:
            return ('pct', attr)
        elif count == 5:
            return ('yds', attr)
        elif count == 6:
            return ('td', attr)
        elif count == 7:
            return ('int', attr)
        elif count == 8:
            return ('rating', attr)
        elif count == 10:
            return ('r_yds', attr)
        elif count == 12:
            return ('td', attr)
        else:
            return -1
        # 1 = att, 2 = yds, 3 = yds/att, 4 = td, 5 = rec, 6 = rec yds, 7 = avg, 8 = td

    if position == 'RB':
        if count == 2:
            return ('att', attr)
        elif count == 3:
            return ('yds', attr)
        elif count == 4:
            return ('avg', attr)
        elif count == 5:
            return ('td', attr)
        elif count == 6:
            return ('rec', attr)
        elif count == 7:
            return ('rec_yds', attr)
        elif count == 9:
            return ('rec_td', attr)
        else:
            return -1
    if position == 'WR' or position == 'TE':
        if count == 1:
            return ('games', attr)
        elif count == 2:
            return ('rec', attr)
        elif count == 3:
            return ('yards', attr)
        elif count == 5:
            return ('td', attr)
        else:
            return -1


def parse_html_nfl(url):
    global t_count
    page = requests.get(url)
    if page.status_code != 200:
        print('NFL NOT 200')
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup.find_all('td')

def attributes(pos, attr, val):
    wr_attr = {'g', 'rec', 'rec_yds', 'rec_td'}
    qb_attr = {'g', 'pass_cmp', 'att', 'pass_yds', 'pass_td', 'pass_int'}
    rb_attr = {'rush_att', 'rush_yds', 'rush_td', 'FUM'}
    def_attr = {'g', 'sacks', 'tackles_combined', 'def_int', 'pass_defended'}
    if pos == 'WR' or pos == 'TE':
        if val in wr_attr:
            return(val, attr)
        return -1
    elif pos == 'QB':
        if val in qb_attr:
            return (val, attr)
        return -1
    elif pos == 'RB':
        if val in rb_attr:
            return (val, attr)
        return -1
    elif pos == 'DEF':
        if val in def_attr:
            return (val, attr)
        return -1


def cipher_nfl_stats(url, pos):
    table = parse_html_nfl(url)
    count = 1
    times = 0
    stats = {}
    # 2 = games 3 = wins 4 = loss 5 = tie 6 = tgt 7 = rec
    try:
        for row in table:
            times += 1
            if ((count > 12 and (pos == 'WR' or pos == 'QB')) or (count > 17 and pos == 'DEF')
                    or (count > 23 and pos == 'RB')):
                break
            val = row.attrs['data-stat']
            for word in row:
                if ((count > 12 and (pos == 'WR' or pos == 'QB')) or (count > 17 and pos == 'DEF')
                        or (count > 23 and pos == 'RB')):
                    break
                attr = word.strip('\n')
                attr = attr.strip(' ')
                attr = attr.strip('\n')
                stat = attributes(pos, attr, val)
                if stat != -1:
                    stats[stat[0]] = stat[1]
                count += 1

    except TypeError:
        print('Type Error')
    return stats

def google_search(query):
    # url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={google_api}&cx={google_cse}'
    # response = requests.get(url)

    search_query = f"site:pro-football-reference.com {query}"
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, params={"q": search_query}, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for result in soup.find_all('a', href=True):
            link = result['href']
            if "pro-football-reference.com" in link:
                return link  # Return the first valid link
    else:
        print("Failed to fetch search results.")
        return None

def get_player_url_nfl(player_name):
    # Search for the player stats page on Pro Football Reference
    query = f"site:pro-football-reference.com {player_name} splits"
    search_results = google_search(query)

    if search_results and 'items' in search_results:
        first_result = search_results['items'][0]
        player_url = first_result['link']
        end = '/splits/'
        split = player_url.split('.htm')
        k = split[0] + end
        return k

# Test with a player name
# cipher_nfl_stats(get_player_url_nfl("Ja'Marr Chase"), 'WR')


#globals
# a list of each dictionary mapping testing category to the player's result
maps = []
college_stats_url = 'https://www.sports-reference.com/cfb/players/'
college_stats_part2 = '/splits/'

def classify(pos, rating):
    if pos == 'QB':
        if rating > 70.0:
            return 'MVP'
        elif rating > 65.0:
            return 'All Pro'
        elif rating > 55.0:
            return 'Starter'
        elif rating > 45.0:
            return 'Below Average Starter'
        else:
            return 'Backup'
    elif pos == 'RB':
        if rating > 51.0:
            return 'All Pro'
        elif rating > 45.0:
            return 'Starter'
        elif rating > 40.0:
            return 'Below Average Starter'
        else:
            return 'Backup'
    elif pos == 'WR':
        if rating > 145.0:
            return 'All Pro'
        elif rating > 100.0:
            return 'Starter'
        elif rating > 60.0:
            return 'Below Average Starter'
        else:
            return 'Backup'
    elif pos == 'TE':
        if rating > 85.0:
            return 'All Pro'
        elif rating > 45.0:
            return 'Starter'
        else:
            return 'Backup'
    elif pos == 'DEF':
        if rating > 90.0:
            return 'MVP'
        if rating > 75.0:
            return 'All Pro'
        elif rating > 55.0:
            return 'Starter'
        else:
            return 'Backup'
    return 0




# calculates qbr for quarterbacks
def qbr(stats):
    # player_statistics = {'Games': 0, 'ATT': 0, 'CMP': 0, 'YDS': 0, 'TD': 0, 'INT': 0}
    completions = float(stats.get('pass_cmp', 0))
    attempts = float(stats.get('att', 0))
    yards = float(stats.get('pass_yds', 0))
    td = float(stats.get('pass_td', 0))
    int = float(stats.get('pass_int', 0))
    if attempts == 0.0:
        return 0
    a = ((completions / attempts) - .3) / .2
    b = ((yards / attempts) - 3) / 4.0
    c = (td / attempts) / .05
    d = (.095 - (int / attempts)) / .04

    return (a + b + c + d) / .06

# calculates rating for running backs
def rbr(stats):
    # player_statistics = {'Games': 0, 'YDS': 0, 'AVG': 0, 'TD': 0, 'FUM': 0}
    att = float(stats.get('rush_att', 0))
    if att == 0:
        return 0
    yards = float(stats.get('yds', 0))
    td = float(stats.get('td', 0))
    fum = float(stats.get('fum', 0))
    ry = (2 * (yards / att) - 5 ) * (1.0 / 3.0)
    rt = td / att * 35
    rf = 2.375 - (55 * (fum / att))
    return ry + rt + rf * (100.0/4.0)


def wrr(stats):
    # player_statistics = {'Games': 0, 'YDS': 0, 'AVG': 0, 'TD': 0, 'REC': 0}
    try:
        g = 0
        if 'g' in stats:
            g = float(stats['g'])
        td = 0
        if 'rec_td' in stats:
            td = float(stats['rec_td'])
        rec_yds = 0
        if 'rec_yds' in stats:
            rec_yds = float(stats['rec_yds'])
        num = ((rec_yds) + 18.0 * td / g / 17.0) / 10.0
        return num
    except ZeroDivisionError:
        return 0

def lbr(stats):
    # player_statistics = {'Games': 0, 'TKL': 0, 'SACK': 0, 'PDEF': 0, 'INT': 0}
    tackles = 0
    if 'tackles_combined' in stats:
        tackles = float(stats['tackles_combined'])
    sacks = 0
    if 'sacks' in stats:
        sacks = float(stats['sacks'])
    pd = 0
    if 'pass_defended' in stats:
        pd = float(stats['pass_defended'])
    interceptions = 0
    if 'def_int' in stats:
        interceptions = float(stats['def_int'])
    games = 0
    if 'g' in stats:
        games = float(stats['g'])
    try:
        num = (tackles * .5 + sacks * 5.0 + pd * 1.5 + 4.0 *
            interceptions / games / 17.0)
        return num
    except ZeroDivisionError:
        return 0


def calculateRating(pos, stats):
    if stats == 0:
        return 0
    if pos == 'QB':
        return classify(pos, qbr(stats))
    elif pos == 'RB':
        return classify(pos, rbr(stats))
    elif pos == 'WR':
        return classify(pos, wrr(stats))
    elif pos == 'TE':
        return classify(pos, wrr(stats))
    elif pos == 'DEF':
        return classify(pos, lbr(stats))


t_count = 0
# takes in full url and returns tables from that url
def parseHTML(url):
    sleep = True
    global t_count
    page = 0
    while sleep:
        page = requests.get(url)
        if page.status_code == 200:
            sleep = False
            t_count += 1
            print(page.status_code)
        else:
            time.sleep(60)
            print('sleeping')
            print(page.status_code)
        if t_count > 10:
            print('sleeping')
            time.sleep(10)
            t_count = 0
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup.find_all('td')


#returns the type of stats to cipher based off of position being passed in
def stats(pos):
    wrs = {'TE', 'WR'}
    defense = {'CB', 'EDGE', 'S', 'LB', 'DT', 'DE'}
    if pos in wrs:
        return 'WR'
    if pos in defense:
        return 'DEFENSE'
    if pos == 'RB':
        return 'RB'
    if pos == 'QB':
        return 'QB'
    return False


def parseCollegeStats(position, count, attr):
    # 0 year, 1 team, 2 games, 3 tackles, 4 solo, 5 ast, 6 sack, 7 safety, 8 pdef, 9 int, 10 tds, 11 yds, 12 avg, 13 lng
    if position == 'DEFENSE':
        if count == 2:
            return ('solo', attr)
        elif count == 4:
            return ('tackles', attr)
        elif count == 5:
            return ('tfl', attr)
        elif count == 6:
            return ('sack', attr)
        elif count == 7:
            return ('int', attr)
        elif count == 10:
            return ('pd', attr)
        else:
            return -1
    # 1 = comp, 2 = attempts, 3 = pct 4 = yds, 5 = td, 6= int, 7 = rate, 8 = att, 9 = yds, 10 = avg, 11 = td
    if position == 'QB':
        if count == 3:
            return ('att', attr)
        elif count == 4:
            return ('pct', attr)
        elif count == 5:
            return ('yds', attr)
        elif count == 6:
            return ('td', attr)
        elif count == 7:
            return ('int', attr)
        elif count == 8:
            return ('rating', attr)
        elif count == 10:
            return ('r_yds', attr)
        elif count == 12:
            return ('td', attr)
        else:
            return -1
        # 1 = att, 2 = yds, 3 = yds/att, 4 = td, 5 = rec, 6 = rec yds, 7 = avg, 8 = td

    if position == 'RB':
        if count == 2:
            return ('att', attr)
        elif count == 3:
            return ('yds', attr)
        elif count == 4:
            return ('avg', attr)
        elif count == 5:
            return ('td', attr)
        elif count == 6:
            return ('rec', attr)
        elif count == 7:
            return ('rec_yds', attr)
        elif count == 9:
            return ('rec_td', attr)
        else:
            return -1
    if position == 'WR' or position == 'TE':
        if count == 1:
            return ('games', attr)
        elif count == 2:
            return ('rec', attr)
        elif count == 3:
            return ('yards', attr)
        elif count == 5:
            return ('td', attr)
        else:
            return -1


# parses college stats
# 1 = att, 2 = yds, 3 = yds/att, 4 = td, 5 = rec, 6 = rec yds, 7 = avg, 8 = td
def cipherCollegeStats(url, pos):
    #rb qb works
    # test wr, te
    table = parseHTML(url)
    count = 1
    times = 0
    stats = []
    try:
        for row in table:
            times += 1
            if count > 11 or (count > 7 and (pos == 'WR' or pos == 'TE')):
                break
            for word in row:
                attr = word.strip('\n')
                attr = attr.strip(' ')
                attr = attr.strip('\n')
                count += 1
                if times > 1:
                    stat = parseCollegeStats(pos, count, attr)
                    if stat != -1:
                        stats.append(stat)
    except TypeError:
        print('Type Error')
    return stats

def file_name(pos):
    return str(pos) + '3.csv'

def exists(name):
    return os.path.exists(name)

def categories(pos):
    if pos == 'TE' or pos == 'WR':
        return ('games', 'rec', 'yards', 'td')
    elif pos == 'QB':
        return ('att', 'pct', 'yds', 'td', 'int', 'rating', 'r_yds', 'td')
    elif pos == 'RB':
        return ('att', 'yds', 'avg', 'td', 'rec', 'rec_yds', 'rec_td')
    elif pos == 'LB' or pos == 'DB' or pos == 'EDGE' or pos == 'CB' or pos == 'DE':
        return ('solo', 'tackles', 'tfl', 'sack', 'int', 'pd')
    else:
        return -1

def outlier(stats, pos):
    if not stats:
        return False
    try:
        if pos == 'TE' or pos == 'WR':
            try:
                rec = float(stats[0][1])
                yards = float(stats[1][1])
                td = float(stats[2][1])
                return rec > 450 or yards > 5500 or td > 65 or rec > yards or td > rec
            except ValueError:
                return True
        elif pos == 'QB':
            try:
                pct = float(stats[1][1])
                yards = float(stats[2][1])
                td = float(stats[3][1])
                int = float(stats[4][1])
                return pct > 100 or yards > 19500 or td > 190 or int > 90
            except ValueError:
                return True
        elif pos == 'RB':
            try:
                yards = float(stats[1][1])
                td = float(stats[3][1])
                rec = float(stats[4][1])
                rec_yds = float(stats[5][1])
                return yards > 7000 or td > 90 or rec > 450 or rec_yds > 5500
            except ValueError:
                return True
        elif pos == 'LB' or pos == 'DB' or pos == 'EDGE' or pos == 'S' or pos == 'CB' or pos == 'DE':
            if stats:
                try:
                    tackles = float(stats[1][1])
                    sack = float(stats[3][1])
                    int = float(stats[4][1])
                    return tackles > 600 or sack > 70 or int > 35
                except ValueError:
                    return True
    except TypeError:
       return False
    return False


def written(pos, cat):
    if not cat[pos]:
        cat[pos] = True
        return False
    else:
        return True

# overall data assignment, call this method to take in a table full of draft data
# returns a tuple with dictionary with keys = testing attribute and value = the player's value, alongside what class
# that player was classified as
def assignData(tables, int_year):
    attributes = {'forty_yd', 'height', 'pos', 'weight', 'shuttle', 'cone', 'broad_jump', 'bench_reps', 'vertical'}
    pos = {'TE' : False, 'WR' : False, 'RB' : False, 'QB' : False, 'LB' : False, 'DB' : False, 'EDGE' : False, 'S' : False, 'CB' : False, 'DE' : False}
    defense = {'LB', 'EDGE', 'DE', 'DT', 'DB', 'CB'}
    player_counter = 1
    player = {}
    for table in tables:
        for row in table:
            dos = table.attrs['data-stat']
            word = row
            if dos == 'college':
                temp = str(word).split('<a href="')
                temp2 = temp[1].split('">')
                word = temp2[0]
            if dos == 'pos':
                if categories(word) != -1:
                    file_n = file_name(word)
                player[dos] = word
            elif dos in attributes:
                player[dos] = word
            if dos == 'draft_info' and 'pos' in player:
                maps.append(player)
                file_n = file_name(player['pos'])
                with open(file_n, 'a') as file:
                    for key, val in player.items():
                        file.write(str(val) + ',')
                player = {'forty_yd' : 0, 'height' : 0, 'weight' : 0, 'shuttle' : 0, 'cone' : 0, 'broad_jump' : 0, 'bench_reps' : 0, 'vertical' : 0, 'college' : 0}
            elif dos == 'college':
                try:
                    words = (row.attrs['href']).split('players/')
                    if len(words) > 1 and categories(player['pos']) != -1 and player['pos'] == 'WR':
                        name = words[1]
                        names = name.split('-')
                        nfl_name = names[0] + ' ' + names[1]
                        nfl_name2 = names[0] + '-' + names[1]
                        college_name = nfl_name2 + '-1'
                        position = player['pos']
                        if position in defense:
                            position = 'DEF'
                        nfl_s = cipher_nfl_stats(parse_name_index(nfl_name), position)
                        rat = calculateRating(position, nfl_s)
                        print(player_counter, ' count')
                        player_counter += 1
                        player['nfl'] = rat
                        college_stats = cipherCollegeStats(college_stats_url + college_name + college_stats_part2, stats(player['pos']))
                        if not outlier(college_stats, player['pos']):
                            player['college'] = college_stats
                        else:
                            player['college'] = 0
                except AttributeError:
                    print('AttributeError')
    return player
    # do an if

# assignData(parseHTML('https://www.pro-football-reference.com/draft/2017-combine.htm'), 2020)
# assignData(parseHTML('https://www.pro-football-reference.com/draft/2016-combine.htm'), 2020)
# assignData(parseHTML('https://www.pro-football-reference.com/draft/2015-combine.htm'), 2020)
# assignData(parseHTML('https://www.pro-football-reference.com/draft/2014-combine.htm'), 2020)
# assignData(parseHTML('https://www.pro-football-reference.com/draft/2013-combine.htm'), 2020)
# assignData(parseHTML('https://www.pro-football-reference.com/draft/2012-combine.htm'), 2020)
# assignData(parseHTML('https://www.pro-football-reference.com/draft/2011-combine.htm'), 2020)

# list of vectors used to maintain player data
player_stats = []

def clean(word):
    try:
        if len(word) > 0:
            trimmed = word.strip(" '\[]()")
            test = float(word)
            return trimmed
        else:
            return 0
    except ValueError:
        cleaned = word.strip(" '\[]()")
        cleaned = cleaned.replace('-', '.')
        try:
            if len(cleaned) > 0:
                test = float(cleaned[0])
                return cleaned
        except ValueError:
            return False

def getFileName(pos):
    base = pos.upper()
    return base + '3.csv'

def max_count(pos):
    if pos == 'QB':
        return 7
    elif pos == 'RB':
        return 7
    elif pos == 'WR' or pos == 'TE':
        return 3
    else:
        return 5

def max_length(pos):
    if pos == 'QB':
        return 16
    elif pos == 'RB':
        return 15
    elif pos == 'WR' or pos == 'TE':
        return 11
    else:
        return 14

def pad(vec, max_length):
    while len(vec) < max_length:
        vec.append(.5)

# normalizes stat value to 0, 1 range
def normalize_stat(count, mins, val):
    if val == 0:
        return .5
    min = mins[count][0]
    max = mins[count][1]
    if max == min:
        min = max - 1
    return (val - min) / (max - min)



def stat_outlier(count, attr):
    if count == 0:
        try:
            speed = float(attr)
            if speed > 4 and speed < 7:
                return False
        except TypeError:
            return True
        return True
    elif count == 1:
        try:
            speed = float(attr)
            if speed > 5.4 and speed < 7.4:
                return False
        except TypeError:
            return True
        return True
    elif count == 2:
        try:
            speed = float(attr)
            if speed > 130 and speed < 500:
                return False
        except TypeError:
            return True
        return True

    elif count == 3:
        try:
            speed = float(attr)
            if speed > 3 and speed < 7:
                return False
        except TypeError:
            return True
        return True

    if count == 4:
        try:
            speed = float(attr)
            if speed > 4 and speed < 9:
                return False
        except TypeError:
            return True
        return True

    if count == 5:
        try:
            speed = float(attr)
            if speed > 80 and speed < 150:
                return False
        except TypeError:
            return True
        return True

    if count == 6:
        try:
            speed = float(attr)
            if speed > 8 and speed < 50:
                return False
        except TypeError:
            return True
        return True

    if count == 7:
        try:
            speed = float(attr)
            if speed > 10 and speed < 600:
                return False
        except TypeError:
            return True
        return True

    if count == 8:
        try:
            speed = float(attr)
            if speed > 50:
                return False
        except TypeError:
            return True
        return True

    return False
# gathers min and max value for each category (used for normalization)
# also gathers mean for category
def normalize(pos, fn):
    #fn = file name
    # val - min / max - min
    minmax = {} # tracks min and max of each attr
    mean = {} # tracks mean of each attr
    # mean : {count : [val, count]}
    with open(fn, mode='r') as file:
        reader = csv.reader(file)
        count = 0
        classification = False
        nextWord = True
        for w in reader:
            for st in w:
                clean_word = clean(st)
                if st == pos:
                    count = 0
                    nextWord = False
                try:
                    if not clean_word == '6' and clean_word != '4':
                        if clean_word == '0' or (float(clean_word) < 7 and float(clean_word) > 3.5) and not st[1] == '-':
                            nextWord = True
                except TypeError or IndexError:
                    f = 1
                if clean_word != False and clean_word != '0' and clean_word is not None and nextWord:
                        if st == pos:
                            classification = True
                            count += 1
                        elif classification:
                            count = 0
                            classification = False
                            nextWord = False
                        else:
                            val = float(clean_word)
                            if val > 25 and count == 1:
                                print(1)
                            if not stat_outlier(count, clean_word) and count < 16:
                                if count in minmax:
                                    if val != 0:
                                        if count in minmax:
                                            if val < minmax[count][0]:
                                                minmax[count][0] = val
                                            elif val > minmax[count][1]:
                                                minmax[count][1] = val
                                            mean[count][0] += val
                                            mean[count][1] += 1
                                else:
                                    if val != 0:
                                        mins = [val, val]
                                        minmax[count] = mins
                                    mean[count] = [val, 1]
                            count += 1
                if clean_word == '0':
                    count += 1
    return minmax, mean

# should probably check if it's within the range and if it's not, just output mean, also get rid of no classifiers


#check to see if more than 5 elements of a vector are missing (inserted as mean)
def five_count(stats):
    five_count = 0
    for st in stats:
        if st == .5:
            five_count += 1
    return five_count > 5



# reads in csv of specified position, and outputs a list of each training vector
# fn = file name
# pos = position
def readCSV(fn, pos):
    global player_stats

    # min and max for each value category
    norms = normalize(pos, fn)
    min_max = norms[0]
    means = norms[1]


    test_stats = []
    with open(fn, mode='r') as file:
        reader = csv.reader(file)
        count = 0
        vec = []
        total_vec = []
        classification = False
        for row in reader:
            for word in row:
                clean_word = clean(word)
                if word == pos:
                    count = 0
                    classification = True
                    continue
                try:
                    float_val = float(clean_word)
                    min = min_max[count][0]
                    max = min_max[count][1]
                    if count < 11 and (float_val < min or float_val > max) and clean_word != False:
                        vec.append(.5)
                        count += 1
                        continue
                except TypeError:
                    g = 1
                if (clean_word != False and clean_word != '0' and clean_word is not None and not stat_outlier(count, clean_word)) or classification:
                    if word == pos:
                        player_stats.append(vec)
                        classification = True
                    elif classification:
                        count = 0
                        if len(vec) < max_length(pos):
                            pad(vec, max_length(pos))
                        total_vec.append(vec)
                        total_vec.append(word)
                        # player_stats.append(total_vec)
                        if not five_count(vec) and word[0].isalpha():
                            test_stats.append(total_vec)
                        vec = []
                        total_vec = []
                        classification = False
                    elif count < 11:
                        clean_word = clean(word)
                        # normalizes stat value
                        norm_word = normalize_stat(count, min_max, float(clean_word))
                        vec.append(norm_word)
                        count += 1
                elif word == '[]':
                    pad(vec, 11)
                elif clean_word == '0' or clean_word == 0 and not clean_word == False:
                    vec.append(.5)
        print(test_stats)
        return test_stats

# if classification != str or .5 count > 6, throw out


# classify z = x * w + b

# pass into softmax y^c = e^zi (z of that class) / sum e^z for each class

# cross entropy loss =

# stochastic gradient descent (update weights)
class multiPerceptron():

    def __init__(self, data):
        self.data = data
        self.x_list = []
        self.y_list = []
        for x, y in data:
            self.x_list.append(x)
            self.y_list.append(y)
        self.x_test = []
        self.y_test = []
        self.model = self.database_model()


    def database_model(self):
        x_train, x_test, y_train, y_test = train_test_split(self.x_list, self.y_list, test_size=0.3, random_state=42)
        self.x_test = x_test
        self.y_test = y_test
        perceptron = Perceptron(max_iter=1000, tol=1e-3, random_state=42, class_weight='balanced')
        perceptron.fit(x_train, y_train)
        return perceptron

    def predict(self, example):
        return self.model.predict(example)


class logisticRegression():
    def __init__(self, data):
        self.data = data
        self.x_list = []
        self.y_list = []
        for x, y in data:
            self.x_list.append(x)
            self.y_list.append(y)
        self.x_test = []
        self.y_test = []
        self.model = self.database_model()

    def database_model(self):
        x_train, x_test, y_train, y_test = train_test_split(self.x_list, self.y_list, test_size=0.3, random_state=42)
        self.x_test = x_test
        self.y_test = y_test
        perceptron = LogisticRegression(max_iter=1000, class_weight='balanced', multi_class='multinomial')
        perceptron.fit(x_train, y_train)
        return perceptron


class randomForest():
    def __init__(self, data):
        self.data = data
        self.x_list = []
        self.y_list = []
        for x, y in data:
            self.x_list.append(x)
            self.y_list.append(y)
        self.x_test = []
        self.y_test = []
        self.model = self.database_model()

    def database_model(self):
        x_train, x_test, y_train, y_test = train_test_split(self.x_list, self.y_list, test_size=0.3, random_state=42)
        self.x_test = x_test
        self.y_test = y_test
        perceptron = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
        perceptron.fit(x_train, y_train)
        return perceptron


class MulticlassPerceptron():
    # x = string (pass in 3 features, one for each position), tuple of chars
    # y = answer
    def __init__(self, examples, iterations):
        self.weight = {}
        self.iterations = iterations
        self.examples = examples
        for example in examples:
            label = example[1]
            self.weight[label] = {}
        for i in range(iterations):
            for x, y in examples:
                prediction = self.predict(x)
                if y != prediction:
                    for key, val in x.items():
                        if key in self.weight[y]:
                            self.weight[y][key] += val
                        else:
                            self.weight[y][key] = val
                        if key in self.weight[prediction]:
                            self.weight[prediction][key] -= val
                        else:
                            self.weight[prediction][key] = -val

    def predict(self, x):
        max_sum = -math.inf
        prediction = None
        for label, pred in self.weight.items():
            temp_sum = 0
            for key in x.keys():
                if key in pred:
                    temp_sum += pred[key] * x.get(key, 0)
            if temp_sum > max_sum:
                max_sum = temp_sum
                prediction = label
        return prediction


complete_set = readCSV(getFileName('WR'), 'WR')
# print(complete_set)

perc = multiPerceptron(complete_set)


accuracy = perc.model.score(perc.x_test, perc.y_test)
print('Multiclass perceptron: ', accuracy)


logistic = logisticRegression(complete_set)
predictions = logistic.model.predict(logistic.x_test)
multiclass_predictions = perc.model.predict(perc.x_test)

forest = randomForest(complete_set)
forest_predictions = forest.model.predict(forest.x_test)
print(forest_predictions, ' forest prediction')
print(forest.y_test, ' actual classifications')

# Evaluate performance
from sklearn.metrics import classification_report
print(classification_report(logistic.y_test, predictions))
print(classification_report(perc.y_test, multiclass_predictions))
print(classification_report(forest.y_test, forest_predictions))


# Multiclass perceptron initial accuracy: 61.39% parameters: max_iter=1000, tol=1e-3, random_state=42
# beware, could just be predicting bust every time, and 61% of players are just busts



norms = normalize('WR', getFileName('WR'))
min_max = norms[0]
aj_stats = [4.57, 6.2, 201.0, 4.36, 7.32, 120.1, 19.0, 33.0, 107, 1749, 14]
norm_stats_aj = []
count = 0
for x in range(11):
    norm_stats_aj.append(normalize_stat(count, min_max, aj_stats[count]))
    count += 1
print(norm_stats_aj, 'aj stats')
prediction = forest.model.predict([norm_stats_aj])
print(prediction, ' Aj prediction')
