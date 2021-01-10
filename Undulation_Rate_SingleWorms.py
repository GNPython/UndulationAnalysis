# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:01:14 2020

@author: GnPro
"""

#this script is designed to be used, after undulation analysis was run, from  where the mean undulation rate ("means") will be provided
# function to obtain undulation ratios for individual worms, from file containing several worms.
def undulation_single(und_data, minutes):
    
    und_means = {}
    # define worm names
    worms = {'A1': 'WT1', 'A2': 'WT2', 'A3': 'WT3', 'A4': 'WT4', 'A5': 'WT5', 'B1': 'WT6', 'B2': 'WT7', 'B3': 'WT8', 
             'B4': 'WT9', 'B5': 'WT10', 'C1': 'WT11', 'C2': 'WT12', 'C3': 'MUT1', 'C4': 'MUT2', 'C5': 'MUT3', 'D1': 'MUT4', 
             'D2': 'MUT5', 'D3': 'MUT6', 'D4': 'MUT7', 'D5': 'MUT8', 'E1': 'MUT9', 'E2': 'MUT10', 'E3': 'MUT11', 
             'E4': 'MUT12', 'E5': 'MUT13'}    
    for c in und_data:
        und_means[c] = {}
        for well in list(worms.keys()):
            worm = worms[well]
            und_event = []
            time = []
            for hour in und_data[c]:
                if hour.endswith(well):
                    und_event += und_data[c][hour]
            if len(und_event) > 0:   
                for t in range(1,len(und_event)+1):
                    time.append(t*minutes)
                und_means[c][worm] = pd.DataFrame(list(zip(time, und_event)),columns = ['Time', 'Undulation_Rate'])
    
    return und_means
    
single = undulation_single(means, binsize)

### The Following section was only used for analysis of manually scored data
scored_worms = []
for well in list(scoring.keys()):
    scored_worms.append(worms[well])

for c in single:
    for e in single[c]:
        if e in scored_worms:
            single[c][e]['How'] = 'Manual'
        else:
            single[c][e]['How']='Tracker'

#creation of df for each group, as well as combined worms, to be used for easier plotting
#condition must be changed to the respective conditions that is desired
single_wt = pd.concat(list(single['cond1'].values()), axis = 0, keys = list(single['cond1'].keys()))
single_wt.reset_index(level = 0, inplace = True)
single_wt.rename(columns = {'level_0':'Worm'}, inplace = True)

single_mut = pd.concat(list(single['cond2'].values()), axis = 0, keys = list(single['cond2'].keys()))
single_mut.reset_index(level = 0, inplace = True)
single_mut.rename(columns = {'level_0':'Worm'}, inplace = True)

single_comb = pd.concat([single_wt, single_mut], axis = 0, keys = ['WT', 'MUT'])
single_comb.reset_index(level = 0, inplace = True)
single_comb.rename(columns = {'level_0':'Cond'}, inplace = True)

#obtain n for all groups
n_wt = int(len(single_wt)/(60/binsize))
n_mut = int(len(single_mut)/(60/binsize))
n_total = n_wt + n_mut

#line plots without errorbars
#just wt
plot = sns.relplot(x='Time', y = 'Undulation_Rate', hue = 'Worm', data = single_wt, palette = pal[0:n_wt], estimator = None, kind = 'line', height = 10, aspect = 1.5)
plot.set(ylim = (0,1.2), xlim =(0,65), title = 'Tracked Undulation ZT8 Wildtypes', xlabel = 'Time [min] \n Data in 3min bins', ylabel = 'Undulation Ratio')

#just mut
plot = sns.relplot(x='Time', y = 'Undulation_Rate', hue = 'Worm', data = single_mut, palette = pal[n_wt:n_total], estimator = None, kind = 'line', height = 10, aspect = 1.5)
plot.set(ylim = (0,1.2), xlim =(0,65), title = 'Tracked Undulation ZT8 Mutants', xlabel = 'Time [min] \n Data in 3min bins', ylabel = 'Undulation Ratio')

#both combined
plot = sns.relplot(x='Time', y = 'Undulation_Rate', hue = 'Worm', data = single_comb, palette = pal[0:n_total], estimator = None, kind = 'line', height = 10, aspect = 1.5)
plot.set(ylim = (0,1.2), xlim =(0,65), title = 'Tracked Undulation ZT8', xlabel = 'Time [min] \n Data in 3min bins', ylabel = 'Undulation Ratio')


#preparation of the data in order to plot averages and add errorbars if desired
plot_ready_single_wt = single_wt.groupby(['Time']).agg(
    Mean = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'mean'),
    SEM = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'sem'),
    N = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'count')).reset_index(level =[0])

plot_ready_single_mut = single_mut.groupby(['Time']).agg(
    Mean = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'mean'),
    SEM = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'sem'),
    N = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'count')).reset_index(level =[0])

plot_ready_single_comb = pd.concat([plot_ready_single_wt, plot_ready_single_mut], keys = ['Tracked_WT', 'Tracked_MUT']).reset_index(level = 0).rename(columns = {'level_0':'Cond'})

#plotting averages (see "PlotManualScorings.py")
