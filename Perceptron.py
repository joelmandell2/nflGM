import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import csv
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.sql.util import expand_column_list_from_order_by


# todo: fix nfl stats so they read from an alternate site if no stats are found
# todo: make sure that
# read in csv data
#todo: normalize combines results


#todo: train model on multiple years of data (only one position per training)
#todo: use multiclass perceptrons, as well as random forest and compare results
#todo: predict based off of model
#todo: graph results

# 1.) Train
# use round as a measure of success
# account for missing data with null values/Average value placement
# get a scale value like height 5'5-7 feet


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
    elif pos == 'CB' or pos == 'S' or pos == 'DE' or pos == 'EDGE' or pos == 'LB' or pos == 'DT':
        if rating > 90.0:
            return 'MVP'
        if rating > 75.0:
            return 'All Pro'
        elif rating > 55.0:
            return 'Starter'
        else:
            return 'Backup'




# calculates qbr for quarterbacks
def qbr(stats):
    # player_statistics = {'Games': 0, 'ATT': 0, 'CMP': 0, 'YDS': 0, 'TD': 0, 'INT': 0}
    completions = float(stats['CMP'])
    attempts = float(stats['ATT'])
    yards = float(stats['YDS'])
    td = float(stats['TD'])
    int = float(stats['INT'])
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
    if stats['ATT'] == 0:
        return 0
    ry = (2 * (stats['YDS'] / stats['ATT']) - 5 ) * (1.0 / 3.0)
    rt = stats['TD'] / stats['ATT'] * 35
    rf = 2.375 - (55 * (stats['FUM'] / stats['ATT']))
    return ry + rt + rf * (100.0/4.0)


def wrr(stats):
    # player_statistics = {'Games': 0, 'YDS': 0, 'AVG': 0, 'TD': 0, 'REC': 0}
    try:
        num = (float(stats['YDS']) + 18.0 * float(stats['TD']) / (float(stats['Games']) / 17.0)) / 10.0
        return num
    except ZeroDivisionError:
        return 0

def lbr(stats):
    # player_statistics = {'Games': 0, 'TKL': 0, 'SACK': 0, 'PDEF': 0, 'INT': 0}
    try:
        num = (float((stats['TKL'])) * .5 + float(stats['SACK']) * 5.0 + float(stats['PDEF']) * 1.5 + 4.0 *
            float(stats['INT'])) / (stats['Games'] / 17.0)
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
    elif pos == 'LB':
        return classify(pos, lbr(stats))
    elif pos == 'EDGE':
        return classify(pos, lbr(stats))
    elif pos == 'DE':
        return classify(pos, lbr(stats))
    elif pos == 'S':
        return classify(pos, lbr(stats))


def scrape_nfl_player_stats(player_name):
    player_stats = {}
    base_url = f'https://www.nfl.com/players/{player_name.lower().replace(" ", "-")}/stats/career'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve stats for {player_name}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    stats_table = soup.find('table', {'class': 'd3-o-table'})

    if not stats_table:
        print(f"No stats table found for {player_name}")
        return None

    player_stats[player_name] = []
    rows = stats_table.find_all('tr')

    for row in rows:
        columns = row.find_all('td')
        if columns:
            stats = [col.get_text(strip=True) for col in columns]
            player_stats[player_name].append(stats)

    return player_stats

def parse_nfl_stats(position, stats):
    if position == 'QB':
        player_statistics = {'Games' : 0, 'ATT' : 0, 'CMP' : 0,'YDS' : 0, 'TD': 0, 'INT' : 0}
        for st in stats:
            if st[3] == '':
                continue
            for i in range(len(st)):
                if i == 2:
                    try:
                        player_statistics['Games'] += int(st[i])
                    except ValueError:
                        player_statistics['Games'] += 0
                elif i == 3:
                    try:
                        player_statistics['ATT'] += float(st[i])
                    except ValueError:
                        player_statistics['ATT'] += 0
                elif i == 4:
                    try:
                        player_statistics['CMP'] += float(st[i])
                    except ValueError:
                        player_statistics['CMP'] += 0
                elif i == 6:
                    try:
                        player_statistics['YDS'] += int(st[i])
                    except ValueError:
                        player_statistics['YDS'] += 0
                elif i == 9:
                    try:
                        player_statistics['TD'] += int(st[i])
                    except ValueError:
                        player_statistics['TD'] += 0
                elif i == 10:
                    try:
                        player_statistics['INT'] += int(st[i])
                    except ValueError:
                        player_statistics['INT'] += 0
        return player_statistics


    elif position == 'RB':
        player_statistics = {'Games' : 0, 'ATT' : 0, 'YDS' : 0, 'AVG' : 0, 'TD': 0, 'FUM' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    try:
                        player_statistics['Games'] += int(st[i])
                    except ValueError:
                        player_statistics['Games'] += 0
                elif i == 3:
                    try:
                        player_statistics['ATT'] += int(st[i])
                    except ValueError:
                        player_statistics['ATT'] += 0
                elif i == 4:
                    try:
                        player_statistics['YDS'] += int(st[i])
                    except ValueError:
                        player_statistics['YDS'] += 0
                elif i == 5:
                    try:
                        player_statistics['AVG'] += float(st[i])
                    except ValueError:
                        player_statistics['AVG'] += 0
                elif i == 7:
                    try:
                        player_statistics['TD'] += int(st[i])
                    except ValueError:
                        player_statistics['TD'] += 0
                elif i == 12:
                    try:
                        player_statistics['FUM'] += int(st[i])
                    except ValueError:
                        player_statistics['FUM'] += 0
        return player_statistics


    elif position == 'WR':
        player_statistics = {'Games' : 0, 'YDS' : 0, 'AVG' : 0, 'TD': 0, 'REC' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    try:
                        player_statistics['Games'] += int(st[i])
                    except ValueError:
                        player_statistics['Games'] += 0
                elif i == 3:
                    try:
                        player_statistics['REC'] += int(st[i])
                    except ValueError:
                        player_statistics['REC'] += 0
                elif i == 4:
                    try:
                        player_statistics['YDS'] += int(st[i])
                    except ValueError:
                        player_statistics['YDS'] += 0
                elif i == 5:
                    try:
                        player_statistics['AVG'] += float(st[i])
                    except ValueError:
                        player_statistics['AVG'] += 0
                elif i == 7:
                    try:
                        player_statistics['TD'] += int(st[i])
                    except ValueError:
                        player_statistics['TD'] += 0
        return player_statistics
    if position == 'DEFENSE':
        player_statistics = {'Games' : 0, 'TKL' : 0, 'SACK' : 0, 'PDEF': 0, 'INT' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    if not st[i] == '':
                        try:
                            player_statistics['Games'] += float(st[i])
                        except ValueError:
                            player_statistics['Games'] += 0

                elif i == 3:
                    if not st[i] == '':
                        try:
                            player_statistics['TKL'] += float(st[i])
                        except ValueError:
                            player_statistics['TKL'] += 0
                elif i == 6:
                    if not st[i] == '':
                        try:
                            player_statistics['SACK'] += float(st[i])
                        except ValueError:
                            player_statistics['SACK'] += 0
                elif i == 8:
                    if not st[i] == '':
                        try:
                            player_statistics['PDEF'] += float(st[i])
                        except ValueError:
                            player_statistics['PDEF'] += 0
                elif i == 9:
                    if not st[i] == '':
                        try:
                            player_statistics['INT'] += int(st[i])
                        except ValueError:
                            player_statistics['INT'] += 0
        return player_statistics

def dot(vec1, vec2):
    return sum(x * y for x, y in zip(vec1, vec2))

# parses the url of the year passed in, returns combine for that year
def getURL(year):
    baseUrl = 'https://www.pro-football-reference.com/draft/'
    extension = str(year) + '-combine.html'
    return baseUrl + extension

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
    return str(pos) + '.csv'

def exists(name):
    return os.path.exists(name)

def categories(pos):
    if pos == 'TE' or pos == 'WR':
        return ('games', 'rec', 'yards', 'td')
    elif pos == 'QB':
        return ('att', 'pct', 'yds', 'td', 'int', 'rating', 'r_yds', 'td')
    elif pos == 'RB':
        return ('att', 'yds', 'avg', 'td', 'rec', 'rec_yds', 'rec_td')
    elif pos == 'LB' or pos == 'DB' or pos == 'EDGE' or pos == 'S' or pos == 'CB' or pos == 'DE':
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
    for table in tables:
        player = {}
        for row in table:
            dos = row.attrs['data-stat']
            for word in row:
                if dos == 'pos':
                    if categories(word) != -1:
                        file_n = file_name(word)

                    player[dos] = word
                elif dos in attributes:
                    player[dos] = word
            if dos == 'draft_info':
                maps.append(player)
                file_n = file_name(player['pos'])
                if exists(file_n):
                    with open(file_n, 'a') as file:
                        for key, val in player.items():
                            file.write(str(val) + ',')
                player = {'forty_yd' : 0, 'height' : 0, 'weight' : 0, 'shuttle' : 0, 'cone' : 0, 'broad_jump' : 0, 'bench_reps' : 0, 'vertical' : 0, 'college' : 0}
            elif dos == 'college':
                try:
                    words = (word.attrs['href']).split('players/')
                    if len(words) > 1 and categories(player['pos']) != -1:
                        name = words[1]
                        names = name.split('-')
                        nfl_name = names[0] + ' ' + names[1]
                        nfl_name2 = names[0] + '-' + names[1]
                        college_name = nfl_name2 + '-1'
                        remains = scrape_nfl_player_stats(nfl_name)
                        nfl_s = 0
                        if not remains is None:
                            for x, y in remains.items():
                                saved = parse_nfl_stats(stats(player['pos']), y)
                                nfl_s = saved
                        rat = calculateRating(player['pos'], nfl_s)
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



# perceptron (true = draft, false = don't)

# need to parse stats to be able to pass in nfl and college stats to signify success or failure
# need to normalize values so that the perceptron can classify based on feature category


# list of vectors used to maintain player data
player_stats = []

def clean(word):
    try:
        if len(word) > 0:
            trimmed = float(word[0])
            return word
        else:
            return 0
    except ValueError:
        cleaned = word.strip(" '\[]()")
        try:
            if len(cleaned) > 0:
                test = float(cleaned[0])
                return cleaned
        except ValueError:
            return False

def getFileName(pos):
    base = pos.upper()
    return base + '.csv'

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
        vec.append(0)

def normalize(stat, count, pos):
    print('COMPLETE ME PLEASE SO I CAN BE PUT OUT OF MY MISSOURI')
    

# reads in csv of specified position, and outputs a list of each training vector
# fn = file name
# pos = position
def readCSV(fn, pos):
    global player_stats
    test_stats = []
    with open(fn, mode='r') as file:
        reader = csv.reader(file)
        count = 0
        vec = []
        total_vec = []
        classification = False
        for row in reader:
            for word in row:
                if count > max_count(pos):
                    if word == pos:
                        player_stats.append(vec)
                        classification = True
                    elif classification:
                        if len(vec) < max_length(pos):
                            pad(vec, max_length(pos))
                        total_vec.append(vec)
                        total_vec.append(word)
                        # player_stats.append(total_vec)
                        test_stats.append(total_vec)
                        vec = []
                        total_vec = []
                        classification = False
                    else:
                        clean_word = clean(word)
                        if clean_word != False:
                            vec.append(clean_word)
                else:
                    count += 1
        print(test_stats)
        return test_stats

readCSV(getFileName('WR'), 'WR')
# print(player_stats)

class BinaryPerceptron():
    def __init__(self, examples, iterations, round):
        # examples is a map of player name to their stats/result
        # set of Tuples(tuple of ((map: name, feature), result)

        # each example is a tuple of 2 pair tuples
        self.weight = {}
        for example in examples:
            for key, item in example[0]:
                self.weight[key] = 0
        # sets the weight of each feature to 0
        for i in range(iterations):
            for x, y in examples:
                totalDot = 0
                for k, v in x.items():
                    totalDot += self.weight[k] * v
                yCurrent = totalDot > 0
                if yCurrent != y:
                    for key, val in x.items():
                        if y:
                            self.weight[key] += val
                        else:
                            self.weight[key] -= val

    # potentially return the grade given from the prediction
    def predict(self, x):
        total = 0
        for key, val in x.items():
            total += dot([self.weight[key]], [val])
        return total > 0

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



