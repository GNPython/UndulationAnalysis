# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math, os
import seaborn as sns

colors = ['deep sea blue', 'dark hot pink', 'british racing green', 'blood', 'cement','pastel purple','vomit green','golden yellow', 'aqua marine', 'coral']
pal = sns.xkcd_palette(colors)
sns.set(context = 'paper', font_scale = 3,)
def move_plot(worms, bins, save = False, **kwargs):

    Bdis = {}
    B2dis = {}
    Hdis = {}
    Tdis = {}
    Bx = []
    By = []
    B2x = []
    B2y = []
    Hx = []
    Hy = []
    Tx = []
    Ty = []
    hours = 0
    for worm in worms:
        hours += 1
        Bx += list(worm.Bx)
        By += list(worm.By)
        B2x += list(worm.B2x)
        B2y += list(worm.B2y)
        Hx += list(worm.Hx)
        Hy += list(worm.Hy)
        Tx += list(worm.Tx)
        Ty += list(worm.Ty)
    print('Name for the plot:')
    plot_name = input()
    
    for n in range(0,len(worm)*hours,bins):
        B = []
        B2 = []
        H = []
        T = []
        for m in range(n, n + bins):
            if m == len(worm)*hours-1:
                continue
            B.append(math.sqrt((Bx[m]- Bx[m+1])**2 + (By[m]-By[m+1])**2))
            B2.append(math.sqrt((B2x[m]- B2x[m+1])**2 + (B2y[m]-B2y[m+1])**2))
            H.append(math.sqrt((Hx[m]-Hx[m+1])**2 + (Hy[m]-Hy[m+1])**2))                    
            T.append(math.sqrt((Tx[m]-Tx[m+1])**2 + (Ty[m]-Ty[m+1])**2))
        Bdis[n/900] = sum(B)/(len(B)/900)
        B2dis[n/900] = sum(B2)/(len(B2)/900)
        Hdis[n/900] = sum(H)/(len(H)/900)
        Tdis[n/900] = sum(T)/(len(T)/900)
    Distances = dict(Body = Bdis, Body2 = B2dis, Head = Hdis, Tail = Tdis)
    disdf = pd.DataFrame(Distances).reset_index(level = 0).rename(columns = {'index':'Time'})
    x=disdf.Time
    fig = plt.figure(figsize = (35,20))
    ax = fig.add_subplot(212)
    ax.plot(x, disdf.Body, label = 'Body', color = pal[0])
    ax.plot(x, disdf.Body2, label = 'Body 2', color = pal[1])
    ax.plot(x, disdf.Head, label = 'Head', color = pal[2])
    ax.plot(x, disdf.Tail, label = 'Tail', color = pal[3])
    ax.legend(title = '', fontsize = 24, loc = 'upper right')
    ax.set_ylabel('Average Distance Moved [px/min] \n Timebin: ' + str(bins/900) +'min', size = 28)
    ax.set_xlabel('Time[min]', size = 28)
    ax.set_title(plot_name, loc = 'center', fontsize = 30, pad = 8)
    
    if len(kwargs) > 0:
        ax.set_title('')
        ax2 = fig.add_subplot(211)
        ax2.set_title(plot_name, loc = 'center', fontsize = 30, pad = 8)
        ax2.bar(x=kwargs['und']['Time'], height=kwargs['und']['Undulation Rate'])
        ax2.set_ylabel('Undulation Ratio', size = 28)
        
    if save == True:
        print('Enter folder where plots should be saved:')
        folder = input()
        location = os.path.join(folder, plot_name)
        fig.savefig(location)
    return fig


plot_this = 'None'
print('Which binsize (in min) do you want to use for plotting movement data?')
bins = int(input())*900
print('Which condition do you want to plot?' + str(list(extr_data.keys())))
cond = input()
print('Enter folder where plots should be saved:')
folder = input()
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
    move_plot(to_plot, bins, und = und)

#3D plots

    # using matplotlib    
# fig = plt.figure(figsize = (18,12))
# ax = fig.add_subplot(111, projection = '3d')
# ax.plot(test.Bx, test.By, zs = test.frame_number, label = 'Body')
# ax.plot(test.B2x, test.B2y, zs = test.frame_number, label = 'Body 2')
# ax.plot(test.Hx, test.Hy, zs = test.frame_number, label = 'Head')
# ax.plot(test.Tx, test.Ty, zs = test.frame_number, label = 'Tail')
# ax.legend(title = '', fontsize = 12, loc = 'lower right')
# ax.set_zlabel('Frame number', size = 12)
# ax.set_xlabel('x', size = 12)
# ax.set_ylabel('y', size = 12)
# ax.set_zscale()
# ax.set_title('Movement Wt - 1', loc = 'center', fontsize = 22, pad = 18)

#    using plotly
fig = px.line_3d(df, x = 'x', y = 'y', z = 'frame_number', color = 'name')
fig.write_html('V2', auto_open = True)