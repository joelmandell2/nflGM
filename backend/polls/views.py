from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from functools import cmp_to_key
import random


#todo: embed model
#todo: get predictions for each player (color by that prediction)

#todo: player page that shows stats of each player
#todo: create a three.js model that takes in time 
# to output a color and based on that color, maps helmet 
#todo: custom player creator
#todo: fix navbar and pages
#fix 2021 receiver, 2025 qb



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
    print('classifying comparator')
    a_comp = a['classification']
    b_comp = b['classification']
    print(a_comp, 'a ', b_comp, ' b')
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
    print(sortBy, ' sort by')
    if sortBy == 'name':
        sorted_list = sorted(json_list, key=lambda x: x['name'])
        return sorted_list
    elif sortBy == 'classification':
        print('about to sort classifier')
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




# NEED TO CHANGE SO THAT IT RETRIEVES YOUR ACTUAL PREDICTION
def random_prediction():
    num = random.randint(1, 5)
    if num == 1:
        return 'All Pro'
    if num == 2:
        return 'Starter'
    if num == 3:
        return 'Below Average Starter'
    else:
        return 'Backup'



#reads in file
def read_file(file_name, sortBy):
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
                count += 1
                if ' ' in f and ')' not in f and '(' not in f and f != 'All Pro' and f != 'Below Average Starter':
                    player_vals['name'] = f.title()
                    player_vals['classification'] = random_prediction()
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
    print('player request made')
    year = request.GET.get('year', 2025) # default is tom brady if none is passed in
    position = request.GET.get('position', 'WR')
    sortBy = request.GET.get('sort', 'name')
    test = 'csv_files/' + str(position) + str(year) + '.csv'
    # file_name = f'csv_files/' + str(position) + str(year) + '.csv'
    print('about to sort')
    total_stats = read_file(test, sortBy)
    # print(total_stats, ' RESPONSE BEING RETURNED IN API')
    return JsonResponse(total_stats, safe=False)

  

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