from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from functools import cmp_to_key
import random
import joblib
import os
import re


#todo: export models for qb, rb
#todo: finish player pages
#todo: custom player creator
#fix 2021 receiver, 2025 qb


#todo: create a three.js model that takes in time 
# to output a color and based on that color, maps helmet 



# reads in file and parses out attributes based on position
# returns a dictionary of trait-val


#comparators used to sort based on attribute

def num_convert(x):
    if x == 'All Pro':
        return 4
    if x == 'Starter':
        return 3
    if x == 'Below Average Starter':
        return 2
    return 1


def prediction_comp(a, b):
    a_comp = a['classification']
    b_comp = b['classification']
    a_num = num_convert(a_comp)
    b_num = num_convert(b_comp)
    return (b_num > a_num) - (a_num > b_num)

def height_comp(a, b):
    a_height = a['Height']
    b_height = b['Height']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    a_height = a_height.replace('-', '.')
    b_height = b_height.replace('-', '.')
    return (float(b_height) > float(a_height)) - (float(a_height) > float(b_height))

def weight_comp(a, b):
    # need to accomodate blank values
    a_height = a['Weight']
    b_height = b['Weight']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (int(b_height) > int(a_height)) - (int(a_height) > int(b_height))


def bench_comp(a, b):
    # need to accomodate blank values
    a_height = a['Bench']
    b_height = b['Bench']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (int(b_height) > int(a_height)) - (int(a_height) > int(b_height))

def broad_comp(a, b):
    # need to accomodate blank values
    a_height = a['Broad']
    b_height = b['Broad']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (int(b_height) > int(a_height)) - (int(a_height) > int(b_height))

def forty_comp(a, b):
    a_height = a['Forty']
    b_height = b['Forty']
    if a_height == ' ':
        a_height = 10000
    if b_height == ' ':
        b_height = 10000
    return (float(a_height) > float(b_height)) - (float(b_height) > float(a_height))

def cone_comp(a, b):
    a_height = a['Cone']
    b_height = b['Cone']
    if a_height == ' ':
        a_height = 10000
    if b_height == ' ':
        b_height = 10000
    return (float(a_height) > float(b_height)) - (float(b_height) > float(a_height))

def shuttle_comp(a, b):
    a_height = a['Shuttle']
    b_height = b['Shuttle']
    if a_height == ' ':
        a_height = 10000
    if b_height == ' ':
        b_height = 10000
    return (float(a_height) > float(b_height)) - (float(b_height) > float(a_height))

def vert_comp(a, b):
    a_height = a['Vertical']
    b_height = b['Vertical']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (float(b_height) > float(a_height)) - (float(a_height) > float(b_height))


# overall sorting function
def sort(json_list, sortBy):
    if sortBy == 'name':
        sorted_list = sorted(json_list, key=lambda x: x['name'])
        return sorted_list
    elif sortBy == 'classification':
        sorted_list = sorted(json_list, key=cmp_to_key(prediction_comp))
        return sorted_list
    elif sortBy == 'Height':
        sorted_list = sorted(json_list, key=cmp_to_key(height_comp))
        return sorted_list
    elif sortBy == 'Weight':
        sorted_list = sorted(json_list, key=cmp_to_key(weight_comp))
        return sorted_list
    elif sortBy == '40 Yard Dash':
        sorted_list = sorted(json_list, key=cmp_to_key(forty_comp))
        return sorted_list
    elif sortBy == 'Shuttle':
        sorted_list = sorted(json_list, key=cmp_to_key(shuttle_comp))
        return sorted_list
    elif sortBy == '3 Cone':
        sorted_list = sorted(json_list, key=cmp_to_key(cone_comp))
        return sorted_list
    elif sortBy == 'Broad Jump':
        sorted_list = sorted(json_list, key=cmp_to_key(broad_comp))
        return sorted_list
    elif sortBy == 'Bench Press':
        sorted_list = sorted(json_list, key=cmp_to_key(bench_comp))
        return sorted_list
    elif sortBy == 'Vertical':
        sorted_list = sorted(json_list, key=cmp_to_key(vert_comp))
        return sorted_list
    return json_list



def load_minmax(position):
    # read in minmax file
    minmax = {}
    file_name = 'norms.csv'
    if position == 'TE':
        file_name = 'normsTE.csv'
    # elif position == 'RB':
    #     file_name = 'norms.RB.csv'
    
    with open('norms.csv', 'r') as file:
        count = 0
        prevWord = ''
        for str in file:
            split_words = str.split(',')
            for word in split_words:
                if word == 'Receptions':
                    word = 'Rec'
                if count == 0:
                    minmax[word] = []
                    prevWord = word
                    count += 1
                else:
                    minmax[prevWord].append(word)
                    count += 1
                if count == 3:
                    count = 0
    return minmax

# read in normalized values 
def normalize(key, val, position):
    if val == 0 or val == ' ':
        return .5
    # need to read in these values
    minmax = load_minmax(position)
    if key == 'Receptions':
        key = 'Rec'
    if key == 'Height':
        val = str(val).replace('-', '.')
    min = float(minmax[key][0])
    max = float(minmax[key][1])
    if max == min:
        min = max - 1
    output = (float(val) - float(min)) / (float(max) - float(min))
    return output




# takes in json and returns the normalized values of each attribute 
def getVector(vals, position):
    normalized_list = []
    for key, val in vals.items():
        if key == 'name':
            return normalized_list
        new_val = normalize(key, val, position)
        new_val = max(new_val, 0.0)
        normalized_list.append(new_val)
    if len(normalized_list) < 11:
        while len(normalized_list < 11):
            normalized_list.append(.5)
    return normalized_list



# NEED TO CHANGE SO THAT IT RETRIEVES YOUR ACTUAL PREDICTION
def random_prediction(js, position):
    #issue is you don't have any stats and the models expect college stats


    forest_wr_model = joblib.load('random_forest_model_wr.pkl')
    logistic_wr_model = joblib.load('logistic_model_wr.pkl')
    #need to read in min/max/mean values
    vec = getVector(js, position)
    x = len(vec)
    while x < 11:
        vec.append(.5)
        x = len(vec)
    forest_prediction = forest_wr_model.predict([vec])
    try:
        # print(forest_prediction, ' FOREST PREDICTION')
        if forest_prediction != 'All Pro' or forest_prediction != 'Backup':
            return logistic_wr_model.predict([vec])
        return forest_prediction
    except Exception as e:
        print(e, ' error')

    # need to pass in vectors to the model
    num = random.randint(1, 5)
    if num == 1:
        return 'All Pro'
    if num == 2:
        return 'Starter'
    if num == 3:
        return 'Below Average Starter'
    else:
        return 'Backup'


def search_file(position, year, name):
    
    return 1



#reads in file
def read_file(file_name, sortBy, position):
    json_vals = []
    
    categories = ['Forty', 'Height', 'Weight', 'Shuttle', 'Cone', 'Broad', 'Bench', 'Vertical']

    try:
        with open(file_name, 'r') as file:
            data = file.read()
            player_vals = {}
            count = 0
            for f in data.split(','):
                if count <= 7:
                    val = f
                    if val == '0':
                        val = ' '
                    player_vals[categories[count]] = val
                elif count < 22 and count > 8:
                    val = f
                    val = re.sub(r'[^0-9.]', '', val)
                    print(val, count, ' count, val')
                    if position == 'RB':
                        if count == 9:
                            player_vals['att'] = val
                        elif count == 11:
                            player_vals['yds'] = val
                        elif count == 13:
                            player_vals['avg'] = float(player_vals['yds']) / float(player_vals['att'])
                        elif count == 15:
                            player_vals['td'] = val
                        elif count == 17:
                            player_vals['rec'] = val
                        elif count == 19:
                            player_vals['r_yds'] = val
                        elif count == 21:
                            player_vals['r_td'] = val
                    elif position == 'QB':

                    else:
                        if val == '':
                            val = ' '
                        if count == 9:
                            player_vals['Receptions'] = val
                        elif count == 11:
                            player_vals['Yards'] = val
                        elif count == 13:
                            player_vals['Touchdowns'] = val
                count += 1
                if ' ' in f and ')' not in f and '(' not in f and f != 'All Pro' and f != 'Below Average Starter':
                    player_vals['name'] = f.title()
                    player_vals['classification'] = random_prediction(player_vals, position)[0]
                    if position == 'RB':
                        if 'att' in player_vals:
                            del player_vals['att']
                        if 'yds' in player_vals:
                            del player_vals['yds']
                        if 'avg' in player_vals:
                            del player_vals['avg']
                        if 'td' in player_vals:
                            del player_vals['td']
                        if 'rec' in player_vals:
                            del player_vals['rec']
                        if 'r_yds' in player_vals:
                            del player_vals['r_yds']
                        if 'r_td' in player_vals:
                            del player_vals['r_td']
                    elif position == 'QB':
                        if 'att' in player_vals:
                            del player_vals['att']
                        if 'pct' in player_vals:
                            del player_vals['pct']
                        if 'yds' in player_vals:
                            del player_vals['yds']
                        if 'td' in player_vals:
                            del player_vals['td']
                        if 'int' in player_vals:
                            del player_vals['int']
                        if 'rating' in player_vals:
                            del player_vals['rating']
                        if 'r_yds' in player_vals:
                            del player_vals['r_yds']
                        if 'r_td' in player_vals:
                            del player_vals['r_td']
                    else:
                        if 'Receptions' in player_vals:
                            del player_vals['Receptions']
                        if 'Yards' in player_vals:
                            del player_vals['Yards']
                        if 'Touchdowns' in player_vals:
                            del player_vals['Touchdowns']
                    json_vals.append(player_vals)
                    player_vals = {}
                    count = 0
    except FileNotFoundError:
        print('file not found error')
    sorted_json = sort(json_vals, sortBy)
    return sorted_json


# views go here
def index(request):
    print('basic request made')
    json = {
        'name' : 'kk',
        'yards' : 10000,
    }
    return JsonResponse(json)



def player(request):

    #need to get position and draft year
    year = request.GET.get('year', 2025) # default is tom brady if none is passed in
    position = request.GET.get('position', 'WR')
    sortBy = request.GET.get('sort', 'name')
    test = 'csv_files/' + str(position) + str(year) + '.csv'
    # file_name = f'csv_files/' + str(position) + str(year) + '.csv'
    total_stats = read_file(test, sortBy, position)
    # print(total_stats, ' RESPONSE BEING RETURNED IN API')
    return JsonResponse(total_stats, safe=False)



def player_page(request):
    name = request.GET.get('p_name', null)
    year = request.GET.get('draft_year', 2025)
    pos = request.GET.get('position', 'QB')
    player_stats = search_file(pos, year, name)
    return JsonResponse(player_stats, safe=False)

  

def draft_year(request):
    print('draft year request made')
    year = request.GET.get('year', 2025)
    json = {
        'players': [{  # Wrap list inside a dictionary
            'name': year,
            'yards': 10000,
        }]
    }
    return JsonResponse(json)