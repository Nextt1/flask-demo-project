import os
import pandas as pd
import numpy as np
from flask_cors import CORS

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

from flask import Flask, jsonify, request
app = Flask(__name__)

CORS(app)

@app.route('/home')
def home():
    headers = ['year', 'level_1', 'level_2', 'value']
    dtypes = {'year': 'float', 'level_1': 'str', 'level_2': 'str', 'value': 'float'}
    df = pd.read_csv( os.path.join(__location__, 'data.csv') , sep=',', header=0, names=headers, dtype=dtypes, na_values=["na"])

    gender = request.args.get('gender')
    year = request.args.get('year')
    
    if not gender:
        gender = 'all'

    if not year:
         year = 2019
    else:
         year = int(year)

    graph_data = df[(df.level_1 != "Total Residents") & (df.level_1 != "Total Male Residents") & (df.level_1 != "Total Female Residents")]
    
    if year == 1970:
        graph_data = graph_data[graph_data["year"] < 1970]
    elif year == 1980:
        graph_data = graph_data[(graph_data["year"] >= 1970) & (graph_data["year"] < 1980)]    
    elif year == 1990:
        graph_data = graph_data[(graph_data["year"] >= 1980) & (graph_data["year"] < 1990)]    
    elif year == 2000:
        graph_data = graph_data[(graph_data["year"] >= 1990) & (graph_data["year"] < 2000)]    
    elif year == 2010:
        graph_data = graph_data[(graph_data["year"] >= 2000) & (graph_data["year"] < 2010)]    
    else:
        graph_data = graph_data[(graph_data["year"] >= 2010)]
    
    if gender == "all":
        graph_data = graph_data[(~graph_data["level_1"].str.contains("Male")) & ((~graph_data["level_1"].str.contains("Female")))]
    elif gender == "male":
        graph_data = graph_data[(graph_data["level_1"].str.contains("Male")) | ((graph_data["level_1"].str.contains("Males")))]
    else:
        graph_data = graph_data[(graph_data["level_1"].str.contains("Female")) | ((graph_data["level_1"].str.contains("Females")))]
    
    graph_data = graph_data.groupby(['year', 'level_1'])
    # c = graph_data['value'].agg(np.sum)
    data = {}

    for i, v in graph_data['value'].agg(np.sum).iteritems():
        t = i[1].replace('Males','').replace("Total Male ","")
        t = t.replace('Females','').replace("Total Female ","")
        t = t.replace('Total','').replace(" Ethnic Groups ()","")
        t = t.strip()
        if i[0] in data:
            data[i[0]][t] = v
            # data[i[0]][t + "Color"] = "hsl(273, 70%, 50%)"
        else:
            data[i[0]] = {
                "year": i[0],
                t: v,
                # t + "Color": "hsl(273, 70%, 50%)",
            }

    return jsonify(
        data=list(data.values())
    )

@app.route('/population')
def population():
    headers = ['year', 'level_1', 'level_2', 'value']
    dtypes = {'year': 'float', 'level_1': 'str', 'level_2': 'str', 'value': 'float'}
    df = pd.read_csv( os.path.join(__location__, 'data.csv') , sep=',', header=0, names=headers, dtype=dtypes, na_values=["na"])

    graph_data = df[(~df["level_2"].str.contains("Over"))]

    gender = request.args.get('gender')
    
    if not gender:
        gender = 'all'

    if gender == "all":
        graph_data = graph_data[graph_data.level_1 == "Total Residents"]
    elif gender == "male":
        graph_data = graph_data[graph_data.level_1 == "Total Male Residents"]
    else:
        graph_data = graph_data[graph_data.level_1 == "Total Female Residents"]

    graph_data = graph_data.groupby(['year', 'level_1'])
    total_population = []

    for i, v in graph_data['value'].agg(np.sum).iteritems():
        
        total_population.append({
            "x": i[0],
            "y":v
        })
    
    return jsonify(
        data=list(total_population)
    )

@app.route('/ethnic_groups')
def ethnicGroupPopulation():
    headers = ['year', 'level_1', 'level_2', 'value']
    dtypes = {'year': 'float', 'level_1': 'str', 'level_2': 'str', 'value': 'float'}
    df = pd.read_csv( os.path.join(__location__, 'data.csv') , sep=',', header=0, names=headers, dtype=dtypes, na_values=["na"])

    graph_data = df[(df.level_1 != "Total Residents") & (~df["level_2"].str.contains("Over"))]

    year = request.args.get('year')
    gender = request.args.get('gender')
    
    if not gender:
        gender = 'all'
    
    if not year:
        year = 2019
    else:
        year = int(year)
    
    graph_data = graph_data[graph_data.year == year]

    if gender == "all":
        graph_data = graph_data[(~graph_data["level_1"].str.contains("Male")) & (~graph_data["level_1"].str.contains("Female"))]
    elif gender == "male":
        graph_data = graph_data[ (graph_data["level_1"] != "Total Male Residents") & (graph_data["level_1"].str.contains("Male"))]
    else:
        graph_data = graph_data[ (graph_data["level_1"] != "Total Female Residents") & (graph_data["level_1"].str.contains("Female"))]

    graph_data = graph_data.groupby(['year', 'level_1'])
    ethnic_population = []

    for i, v in graph_data['value'].agg(np.sum).iteritems():
        
        t = i[1].replace('Total','').replace(" Ethnic Groups ()","")
        t = t.replace("Males",'').replace("Male",'').replace("Females",'').replace("Female",'')
        t = t.strip()
        
        ethnic_population.append({
            "id": t,
            "label": t,
            "value": v
        })
    
    return jsonify(
        data=list(ethnic_population)
    )

@app.route('/age_groups')
def ageGroupPopulation():
    headers = ['year', 'level_1', 'level_2', 'value']
    dtypes = {'year': 'float', 'level_1': 'str', 'level_2': 'str', 'value': 'float'}
    df = pd.read_csv( os.path.join(__location__, 'data.csv') , sep=',', header=0, names=headers, dtype=dtypes, na_values=["na"])

    graph_data = df[(df.level_1 != "Total Residents") & (~df["level_2"].str.contains("Over"))]

    year = request.args.get('year')
    gender = request.args.get('gender')
    
    if not gender:
        gender = 'all'
    
    if not year:
        year = 2019
    else:
        year = int(year)
    
    graph_data = graph_data[graph_data.year == year]

    if gender == "all":
        graph_data = graph_data[(~graph_data["level_1"].str.contains("Male")) & (~graph_data["level_1"].str.contains("Female"))]
    elif gender == "male":
        graph_data = graph_data[ (graph_data["level_1"] != "Total Male Residents") & (graph_data["level_1"].str.contains("Male"))]
    else:
        graph_data = graph_data[ (graph_data["level_1"] != "Total Female Residents") & (graph_data["level_1"].str.contains("Female"))]

    graph_data = graph_data.groupby(['year', 'level_2'])

    age_population = []

    for i, v in graph_data['value'].agg(np.sum).iteritems():
        
        t = i[1].replace('Total','').replace(" Ethnic Groups ()","")
        t = t.replace("Years", '').strip()

        
        age_population.append({
            "age group": t,
            "population": v
        })
    
    if len(age_population) > 9:
        age_population.insert(1, age_population.pop(9))
        
    return jsonify(
        data=list(age_population)
    )

    if __name__ == "__main__":
        app.run()
