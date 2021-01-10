# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math, os, natsort, re
import seaborn as sns
import numpy as np
colors = ['deep sea blue', 'dark hot pink', 'british racing green', 'blood', 'cement','pastel purple','vomit green','golden yellow', 'aqua marine', 'coral']
pal = sns.xkcd_palette(colors)
sns.set(context = 'paper', font_scale = 3,)

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



# def manvsmachine(machine, man, save = False):
#     print('Name for the plot:')
#     plot_name = input()
#     plot_data = pd.concat([machine, man], keys=['Tracked','Manual'])
#     plot_data.reset_index(level=0, inplace = True)
#     plot_data.rename(columns = {'level_0':'Source'}, inplace = True)
#     fig = sns.barplot(data = plot_data, x = 'Time', y='Undulation_Rate', hue = 'Source', )
#     fig.set(title = plot_name)
#     if save == True:
#         print('Enter folder where plots should be saved:')
#         folder = input()
#         location = os.path.join(folder, plot_name)
#         fig.savefig(location)
#     return fig

def manvsmachine(machine, man, save = False):
    print('Name for the plot:')
    plot_name = input()
    
    fig = plt.figure(figsize = (35,20))
    fig.suptitle(plot_name)
    ax = fig.add_subplot(211)
    ax.set_title('Machine', loc = 'center', fontsize = 30, pad = 8)
    ax.bar(x=machine['Time'], height=machine['Undulation_Rate'], color = pal[6])
    ax.set_ylabel('Undulation Ratio', size = 28)
    ax.set_ylim(0,1)
    ax.set_xlim(0, 65)
    ax.set_xticks(np.arange(0,65,5))
    ax2 = fig.add_subplot(212)
    ax2.bar(x = man['Time'], height = man['Undulation_Rate'], color = pal [3])
    ax2.set_title('Human', loc = 'center', fontsize = 30, pad = 8)
    ax2.set_ylabel('Undulation Ratio', size = 28)
    ax2.set_xlim(0,65)
    ax2.set_xticks(np.arange(0,65,5))
    ax2.set_ylim(0,1)    
    ax2.set_xlabel('Time [min] \n (Data in 3 minute bins)', size = 28)
    if save == True:
        print('Enter folder where plots should be saved:')
        folder = input()
        location = os.path.join(folder, plot_name)
        fig.savefig(location)
    return fig


plot_this = 'None'
print('Which condition do you want to plot?' + str(list(extr_data.keys())))
cond = input()
while plot_this != '':
    print('Enter the well name for worm to plot: \n' + str(list(extr_data[cond].keys())))
    print('(Press "Enter" to quit.)')
    plot_this = input()
    if plot_this == '':
        continue
    to_plot = []
    for w in extr_data[cond]:
        if str(w).endswith(plot_this):
            to_plot.append(extr_data[cond][w])
    und = single[cond][worms[plot_this]]
    und_manual = und_rate_man[plot_this]    
    manvsmachine(und, und_manual, save = True)