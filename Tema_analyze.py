from flask import Flask, render_template, request
import requests
import pandas as pd
import os
import getpass
import sys
from openpyxl import Workbook
from openpyxl import load_workbook

app = Flask(__name__)

def download_file(url, output_path):
    response = requests.get(url)
    with open(output_path, 'wb') as file:
        file.write(response.content)

def get_platform_path(username, path):
    if sys.platform == 'win32':
        return f'C:/Users/{username}/Documents/{path}'
    elif sys.platform == 'darwin':
        return f'/Users/{username}/Documents/{path}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    team = request.form['team']
    username = getpass.getuser()
    pdata_file_url = 'https://drive.google.com/uc?id=13vVpc0a87eyqUDyISthnx4TP8XfrAmyB'
    tdata_file_url = 'https://drive.google.com/uc?id=1gEshT9oOmnEbrqfuSYn9T09BFfokH1Ye'
    pdata_output_path = get_platform_path(username, 'Pdata_file.csv')
    tdata_output_path = get_platform_path(username, 'Tdata_file.csv')

    download_file(pdata_file_url, pdata_output_path)
    download_file(tdata_file_url, tdata_output_path)

    try:
        pdata = pd.read_csv(pdata_output_path)
    except FileNotFoundError:
        pdata = pd.DataFrame()
    
    try:
        tdata = pd.read_csv(tdata_output_path)
    except FileNotFoundError:
        tdata = pd.DataFrame()

    P_namedata = pdata[['NAME', 'TEAM']].copy()
    P_stats = []
    max_stats = []

    result_data = P_namedata.iloc[:10, :3]
    result_Teamdata = tdata.loc[tdata['TEAM_NAME'] == team]

    return render_template('result.html', team=result_Teamdata)

@app.route('/result2', methods=['POST'])
def result2():
    stats = request.form.getlist('stats')
    team = request.form['team']

    username = getpass.getuser()
    pdata_file_url = 'https://drive.google.com/uc?id=13vVpc0a87eyqUDyISthnx4TP8XfrAmyB'
    tdata_file_url = 'https://drive.google.com/uc?id=1gEshT9oOmnEbrqfuSYn9T09BFfokH1Ye'
    pdata_output_path = get_platform_path(username, 'Pdata_file.csv')
    tdata_output_path = get_platform_path(username, 'Tdata_file.csv')

    download_file(pdata_file_url, pdata_output_path)
    download_file(tdata_file_url, tdata_output_path)

    pdata = pd.read_csv(pdata_output_path)
    tdata = pd.read_csv(tdata_output_path)

    P_namedata = pdata[['NAME', 'TEAM']].copy()
    P_stats = []
    max_stats = []

    def arrange(stats): 
        selected_cols = ['NAME', stats]
        selected_data = pdata[selected_cols]
        if stats == 'TOV' or stats == 'PF':
            sorted_data = selected_data.sort_values(by=stats, ascending=True)
        else:
            sorted_data = selected_data.sort_values(by=stats, ascending=False)
        sorted_data.reset_index(drop=True, inplace=True) 
        sorted_data[stats] = sorted_data[stats].rank(method='max', ascending=True) 
        return sorted_data[['NAME', stats]]

    P_stats = stats

    for i in range(len(P_stats)):
        merged_data = pd.merge(P_namedata, arrange(P_stats[i]), on='NAME', how='outer')
        P_namedata = merged_data

    P_namedata['sum_score'] = P_namedata.iloc[:, 2:].sum(axis=1) 
    P_namedata = P_namedata.sort_values(by='sum_score', ascending=False) 

    max_stats = P_namedata.iloc[:, 2:-1].idxmax(axis=1) 
    melted_data = P_namedata.melt(id_vars=['NAME', 'TEAM'], value_vars=max_stats, var_name='stat', value_name='max_value') 
    P_namedata['max'] = melted_data.loc[melted_data.groupby(['NAME'])['max_value'].idxmax(), 'stat']
    P_namedata.insert(2, 'max_stats', max_stats)

    condition = (P_namedata['TEAM'] != team) 
    P_namedata = P_namedata[condition]

    P_namedata.reset_index(drop=True, inplace=True)
    P_namedata.index = P_namedata.index + 1

    result_data = P_namedata.iloc[:10, :3]
    result_Teamdata = tdata.loc[tdata['TEAM_NAME'] == team]

    return render_template('result2.html', team=result_Teamdata, result_data=result_data)

if __name__ == '__main__':
    app.run(debug=True)
