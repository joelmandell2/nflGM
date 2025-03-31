def read_file(file_name):
    json_vals = []
    
    categories = ['40 Yard Dash', 'Height', 'Weight', 'Shuttle', '3 Cone', 'Broad Jump', 'Bench', 'Vertical']


    with open(file_name, 'r') as file:
       data = file.read()
       player_vals = {}
       count = 0
       for f in data.split(','):
           print(f)
           if count <= 7:
               val = f
               if val == '0':
                   val = ' '
               player_vals[categories[count]] = val
           count += 1
           if ' ' in f and ')' not in f and '(' not in f:
               player_vals['name'] = f.title()
               json_vals.append(player_vals)
               player_vals = {}
               count = 0
    return json_vals



read_file('csv_files/WR2025.csv')