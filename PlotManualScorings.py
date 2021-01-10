# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math, os, natsort, re
import seaborn as sns
import numpy as np

#settings for plots
colors = ['deep sea blue', 'dark hot pink', 'british racing green', 'blood', 'cement','pastel purple','vomit green','golden yellow', 'aqua marine', 'coral']
pal = sns.xkcd_palette(colors)
sns.set(context = 'paper', font_scale = 3)

#worm identities
worms = {'A1': 'WT1', 'A2': 'WT2', 'A3': 'WT3', 'A4': 'WT4', 'A5': 'WT5', 'B1': 'WT6', 'B2': 'WT7', 'B3': 'WT8', 
         'B4': 'WT9', 'B5': 'WT10', 'C1': 'WT11', 'C2': 'WT12', 'C3': 'MUT1', 'C4': 'MUT2', 'C5': 'MUT3', 'D1': 'MUT4', 
         'D2': 'MUT5', 'D3': 'MUT6', 'D4': 'MUT7', 'D5': 'MUT8', 'E1': 'MUT9', 'E2': 'MUT10', 'E3': 'MUT11', 
         'E4': 'MUT12', 'E5': 'MUT13'}  

#get scoring data
scoring =  {}
print('Where is your scoring data?')
score_loc = input()
file_list = natsort.natsorted(os.listdir(score_loc))
score_files = []
for file in file_list:
    if file.endswith('.csv'):
        score_files.append(file)
for score_file in score_files:
    scoring[score_file[-6:-4]]=pd.read_csv(score_loc + '\\' + score_file)
print('Enter binsize for undulation rate in minutes:')
bins = int(input())*900
und_rate_man = {}
frames = 54000
first_frame = 0
for e in scoring:
    df = scoring[e]
    start = list(df[df['Behaviour']=='Undulation'].Start_Frame)
    stop = list(df[df['Behaviour']=='Undulation'].Stop_Frame)
    undulation = {}
    count = {}
    for f in range(frames):
        for i in range(len(start)):
            if f >= start[i] and f <= stop[i]:
                undulation[f] = True
    for fr in range(first_frame, frames, bins):
        x =(fr+bins)/900
        count[x] = 0
        for fra in range(fr, fr + bins):
            if fra in undulation.keys():
                count[x] += 1
        count[x] /= bins
    und_rate_man[e] = pd.DataFrame(dict(Time=list(count.keys()), Undulation_Rate=list(count.values())))

und_rate_man_wt = {}
und_rate_man_mut = {}
for und in und_rate_man:
    if worms[und].startswith('WT'):
        und_rate_man_wt[worms[und]] = und_rate_man[und]
    elif worms[und].startswith('MUT'):
        und_rate_man_mut[worms[und]] = und_rate_man[und]
    else:
        continue
    
#get number of scored worms
num_worms = len(und_rate_man)
num_wt = len(und_rate_man_wt)
num_mut = len(und_rate_man_mut)

#split data into corresponding dfs
und_rate_man_wt = pd.concat(und_rate_man_wt.values(), axis = 0, keys = und_rate_man_wt.keys())
und_rate_man_wt.reset_index(level=0, inplace = True)
und_rate_man_wt.rename(columns = {'level_0':'Worm'}, inplace = True)

und_rate_man_mut = pd.concat(und_rate_man_mut.values(), axis = 0, keys = und_rate_man_mut.keys())
und_rate_man_mut.reset_index(level=0, inplace = True)
und_rate_man_mut.rename(columns = {'level_0':'Worm'}, inplace = True)

und_rate_man_comb = pd.concat(und_rate_man.values(), axis = 0, keys = scored_worms)
und_rate_man_comb.reset_index(level = 0, inplace = True)
und_rate_man_comb.rename(columns = {'level_0':'Worm'},inplace = True)

#Plot single data
plot = sns.relplot(x='Time', y = 'Undulation_Rate', hue = 'Worm', data = und_rate_man_comb, palette = pal[0:num_worms], estimator = None, kind = 'line', height = 10, aspect = 1.5,)
plot.set(ylim = (0,1.2), xlim =(0,65), title = 'Manually Scored Undulation ZT8', xlabel = 'Time [min] \n Data in 3min bins', ylabel = 'Undulation Ratio')

plot = sns.relplot(x='Time', y = 'Undulation_Rate', hue = 'Worm', data = und_rate_man_wt, palette = pal[0:num_wt], estimator = None, kind = 'line', height = 10, aspect = 1.5,)
plot.set(ylim = (0,1.2), xlim =(0,65), title = 'Manually Scored Undulation ZT8', xlabel = 'Time [min] \n Data in 3min bins', ylabel = 'Undulation Ratio')

plot = sns.relplot(x='Time', y = 'Undulation_Rate', hue = 'Worm', data = und_rate_man_mut, palette = pal[num_wt:num_worms], estimator = None, kind = 'line', height = 10, aspect = 1.5,)
plot.set(ylim = (0,1.2), xlim =(0,65), title = 'Manually Scored Undulation ZT8', xlabel = 'Time [min] \n Data in 3min bins', ylabel = 'Undulation Ratio')

#get averages
plot_ready_man_wt = und_rate_man_wt.groupby(['Time']).agg(
    Mean = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'mean'),
    SEM = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'sem'),
    N = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'count')).reset_index(level =[0])

plot_ready_man_mut = und_rate_man_mut.groupby(['Time']).agg(
    Mean = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'mean'),
    SEM = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'sem'),
    N = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'count')).reset_index(level =[0])

plot_ready_man_comb = pd.concat([plot_ready_man_wt, plot_ready_man_mut], keys = ['Manual_WT', 'Manual_MUT']).reset_index(level = 0).rename(columns = {'level_0':'Cond'})

#plot averages (to compare between tracked and scored data) this requires the script "Undulation_Rate_SingleWorms.py" to be run before
#in order to obtain the plot-ready data for single worms provided by the tracker

plottable_wt = pd.concat([plot_ready_single_wt,plot_ready_man_wt], keys = ['Tracked','Manual'], axis = 0).reset_index(level=0).rename(columns={'level_0':'How'})

plottable_mut = pd.concat([plot_ready_single_mut,plot_ready_man_mut], keys = ['Tracked','Manual'], axis = 0).reset_index(level=0).rename(columns={'level_0':'How'})

plottable_comb = pd.concat([plot_ready_single_comb,plot_ready_man_comb], keys = ['Tracked','Manual'], axis = 0).reset_index(level=0).rename(columns={'level_0':'How'})

#Wildtypes
plot = sns.FacetGrid(plottable_wt, height = 10, aspect = 1.5, palette = pal, hue = 'How')
plot.map(plt.errorbar, 'Time','Mean','SEM', fmt = 'o')
plot.set(ylim=(0,1),xlim=(0,max(plottable_wt['Time'])+1), xlabel = 'Time [min] \n Data in 3min bins', ylabel= 'Undulation Ratio', xticks = np.arange(0,63,3),
         title = 'Undulation Averages Wildtype')
plot.add_legend(title = '')

#Mutant
plot = sns.FacetGrid(plottable_mut, height = 10, aspect = 1.5, palette = pal, hue = 'How')
plot.map(plt.errorbar, 'Time','Mean','SEM', fmt = 'o')
plot.set(ylim=(0,1),xlim=(0,max(plottable_mut['Time'])+1), xlabel = 'Time [min] \n Data in 3min bins', ylabel= 'Undulation Ratio', xticks = np.arange(0,63,3),
         title = 'Undulation Averages Mutant')
plot.add_legend(title = '')

#All
plot = sns.FacetGrid(plottable_comb, height = 10, aspect = 1.5, palette = pal, hue = 'Cond')
plot.map(plt.errorbar, 'Time','Mean','SEM', fmt = 'o')
plot.set(ylim=(0,1),xlim=(0,max(plottable_comb['Time'])+1), xlabel = 'Time [min] \n Data in 3min bins', ylabel= 'Undulation Ratio', xticks = np.arange(0,63,3),
         title = 'Undulation Averages')
plot.add_legend(title = '')
