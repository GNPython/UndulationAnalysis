#! Python3

# This Script can be used to load, modify and analyse
# tracking files created by the deep learning software "loopy" by LoopBio GmbH
# incorporating the possibility to analyse undulation behaviour for user-defined
# bodyparts. 

# required packages
import re, os, natsort, math
import pandas as pd
import scipy.signal as sp
from scipy.stats import shapiro, ttest_ind, mannwhitneyu, ttest_rel, wilcoxon
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from sklearn import metrics

### Defining necessary functions

# Extract data from a given location, creating a dictionary that contains a
# dataframe with all needed datapoints for every well in every video
def data_extraction(dataset):
    # Define regular expression to fit tracking file
    track_file = re.compile(r""" ^(\w+)         #date
                                    (\d{6})     #video number
                                    (\w{2}\d)   #well number
                                    (\w+)       #everything after
                                    """,re.VERBOSE)
    
    file_list = natsort.natsorted(os.listdir(dataset))

    all_data = {}
    
    for datasheet in file_list:
        
        # get video number and well number from file name
        mo = track_file.search(datasheet)
        if mo == None:
            continue
        well_num  = mo.group(3)
        vid_num = mo.group(2)
          
        # read in data and reformat to make it more readable
        # unnecessary information will be removed, all coordinates will be shown as
        # columns for every frame
        df = pd.read_csv(dataset + '\\' + datasheet)
        df = df.pivot(index = 'frame_number', columns = 'name', values = ['x', 'y'])
        
        # put all data into one dictionary using hour and well as index
        all_data[vid_num + well_num] = df
    
    return all_data
     
# function to check if coverage is >90%, creates list of wells where tracking is 
# <90% and suggests them for exclusion from analysis
def check_track(data, frames):
    ex_well = []
    
    for c in data:
       for e in data[c]:
           if e[-2:] in ex_well:
               continue
           else:
                nums = list(data[c][e].x.count()<(frames*0.9))
   
           if any(nums):
               ex_well.append(e[-2:])
        
    print('The following wells do not show complete tracking, thus are suggested to be excluded from analysis'
          , ex_well, sep = '\n')
    return ex_well

# function to actually remove the badly tracked datasets from the analysis
def remove_data(data, exclude):
        for c in data:
            remove = []
            
            for e in data[c]:
                if e[-2:] in exclude:
                    remove.append(e)
                    
            for rem in remove:
                del data[c][rem]
        return None
    
# function to extract indices of dominant undulation frequencies (depending on binsize) 
# for user-defined list of bodypoints
def frequencies(data, frames, bins, points, low = 4, up = 17):
    freq_list = {}
    for c in data:
        freq_list[c] = {}
        for e in data[c]:
            l = []
            for point in points:
                x_cords = list(data[c][e].x[point])
                y_cords = list(data[c][e].y[point])
                for n in range(0,frames,bins):
                    x_l = x_cords[n:n+bins]
                    y_l = y_cords[n:n+bins]
                    x = {}
                    y = {}
                    dis_moved = math.sqrt((max(x_l) - min(x_l))**2 + (max(y_l)-min(y_l))**2)     
                    
                    # ensures that we only extract frequency if the 
                    # movement of the point is within undulation range
                    if   0.5 < dis_moved < 15:  
                        x['f'], x['s'] = sp.periodogram(x_l, fs = 15)
                        if max(x['s'][low:up]) > max(x['s'][0:low]):
                            l.append(n)
                            continue # if undulation is detected for x, 
                                     # we don't want to check it for y anymore!
                        y['f'], y['s'] = sp.periodogram(y_l, fs = 15)
                        if max(y['s'][low:up]) > max(y['s'][0:low]):
                            l.append(n)
                    else:
                        continue
                    
            # a list is created containing starting frame of a undulation-positive bin
            l = list(set(l))     
            l.sort()
            freq_list[c][e] = l
    return freq_list

# function for binning data according to specified binsize, calculates mean for every bin
def binning (data, binm, hours, worms, mean_factor):
    binned = {}
    bin_hour = int((60*hours)/binm)
    
    for c in data:
        binned[c] = {}
        for e in data[c]:
            b_start = 0
            b_end = binm*900
            binned[c][e] = {}
            bini = 0
            for bini in range(1,bin_hour+1):
                binned[c][e][bini]=[]
                for f in range(len(data[c][e])):
                    if b_start <= data[c][e][f] and data[c][e][f] < b_end:
                        binned[c][e][bini].append(data[c][e][f])
                    else:
                        continue
                b_start = b_end
                b_end += binm*900           
    means = {}
    for c in binned:
        means[c] = {}
        for e in binned[c]:
            means[c][worms[e[-2:]]] = []
            for b in binned[c][e]:
                means[c][worms[e[-2:]]].append(len(binned[c][e][b])/(mean_factor*binsize))
            means[c][worms[e[-2:]]] = pd.DataFrame(means[c][worms[e[-2:]]])
            means[c][worms[e[-2:]]].reset_index(level = 0, inplace = True)
            means[c][worms[e[-2:]]].rename(columns = {'index':'Time', 0:'Undulation_Rate'}, inplace = True)
            means[c][worms[e[-2:]]]['Time'] = means[c][worms[e[-2:]]]['Time'].apply(lambda a: (a+1)*binm)
                
    return binned, means

# function to prepare data for plotting, takes data for all conditions, lets user define a proper name for the condition
# creates dataframe which contains the average time spent undulating for all time-bins ('Mean'), the standard error of the mean ('SEM'),
# the number of worms within the group ('N'), as well as the specified name for the group ('Group').
# Additionally, the area under the curve (AUC)for every worm is calculated and stored in a separate dataframe.           
def plot_prep(mean_data, conds):
    data_prepped = {}
    areas = []
    for c in conds:
        # data for undulation ratios plot
        cond_name = input('Please specify a name for condition ' + str(c) +': ')
        cond_pos = 'cond' + str(c)
        data_prepped[c] = pd.concat(mean_data[cond_pos]).reset_index(level = 0).rename(columns = {'level_0':'Worm'})
        data_prepped[c]['Group'] = cond_name
        
        # data for area under the curve
        for w in mean_data[cond_pos]:
            row = {}
            row['Group'] = cond_name
            row['Worm'] = w
            row['AUC'] = metrics.auc(mean_data[cond_pos][w]['Time'], 
                                     mean_data[cond_pos][w]['Undulation_Rate'])
            areas.append(row)
        
    plot_ready = pd.concat(data_prepped).groupby(['Group', 'Time']).agg(
        Mean = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'mean'),
        SEM = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'sem'),
        N = pd.NamedAgg(column = 'Undulation_Rate', aggfunc = 'count')).reset_index(level =[0,1])
    
    areas = pd.DataFrame(areas, columns = ['Group', 'Worm', 'AUC']).sort_values(by = ['Group','Worm'])
    
    return plot_ready, areas

# function to check AUC-values for normality for each group
def check_normal(AUC_data):
    normality = {}
    AUC_dict = {}
    grouped_AUC = AUC_data.groupby('Group')
    for x in list(AUC_data['Group'].unique()):
        cond = x
        AUC_dict[cond] = grouped_AUC.get_group(x)['AUC']
    for s in AUC_dict:
        if shapiro(AUC_dict[s])[1] > 0.05:
            normality[s] = 'Yes'
        else:
            normality[s] = 'No'
    return normality

# function to compare specified conitions using the appropriate statistical test
def stat_test(AUC_data, conds, normal, ind):
    grouped_AUC = AUC_data.groupby('Group')
    
    c1 = conds[0]
    c2 = conds[1]
    
    c1_data = grouped_AUC.get_group(c1)['AUC']
    c2_data = grouped_AUC.get_group(c2)['AUC']
    
    if normal[c1] == 'Yes' and normal[c2] == 'Yes':
        parametric = True
    else:
        parametric = False
    
    if parametric and ind == 'y':
        s, p = ttest_ind(c1_data, c2_data)
        test = 't-test'
    elif not parametric and ind == 'y':
        s, p = mannwhitneyu(c1_data, c2_data)
        test = 'Mann-Whitney'
    elif parametric and ind != 'y':
        s, p = ttest_rel(c1_data, c2_data)
        test = 't-test'
    else:
        s, p = wilcoxon(c1_data, c2_data)
        test = 'Wilcoxon'
    
    if p < 0.05:
        result = str(c1) + ' vs ' + str(c2) + ' is significantly different. ('+ test + ': p-value = ' + str(p) + ')'
    else:
        result = str(c1) + ' vs ' + str(c2) + ' is NOT significantly different. ('+ test + ': p-value = ' + str(p) + ')'
    
    return result

# function to plot data
def plotting(plot_data, area_data, plus_auc = 'y'):
    label_x = input('Specify x-axis label: ')
    start_x = int(input('Specify starting timepoint for x-axis: '))
    fig_title = input('Specify figure title: ')
    label_y ='Undulation Ratio'
    t_start = int(min(plot_data['Time']))
    t_end = int(max(plot_data['Time']))
    total_time = int(t_end/60)
    plot = sns.FacetGrid(plot_data, height = 10, aspect = 1.5, palette = pal, hue = 'Group')
    plot.map(plt.errorbar, 'Time', 'Mean', 'SEM', fmt = 'o')
    plot.set(ylim=(0,1),xlim=(0,max(plot_data['Time'])+5), xlabel = label_x, 
             ylabel= label_y, xticks = np.arange(t_start,t_end, t_end/(total_time)),
             xticklabels = np.arange(start_x,start_x+total_time,1), title = fig_title)
    plot.add_legend(title = '')

    if plus_auc == 'y':
        saver = True
        plot2 = sns.catplot(x = 'Group', y ='AUC', hue = 'Group', data = area_data, 
                           palette = pal, height = 10, aspect = 0.8, kind = 'box', dodge = False)
        plot2.add_legend(title = '', loc = 'lower center', ncol = 2)
        plot2 = sns.swarmplot(x ='Group', y = 'AUC', data = area_data,size = 10)
        plot2.set(xlabel= '', title = fig_title , xticklabels = '')
        
    ans = input('Do you wish to save the plot(s)? (y/n) \n').lower()
    if ans == 'y':
        path = input('Enter filepath: \n')
        date = dt.datetime.now()
        date = date.strftime('%Y%m%d')
        output_name = date + '_' + fig_title + '.png'
        output = os.path.join(path, output_name)
        plot.savefig(output)
        if saver == True:
            output_name2 = date + '_' + fig_title + '_AUC.png'
            output2 = os.path.join(path, output_name2)
            plot2.get_figure().savefig(output2)
    return plot, plot2

# define plate set-up
Common = {'A1': 'WT01', 'A2': 'WT02', 'A3': 'WT03', 'A4': 'WT04', 'A5': 'WT05', 
          'B1': 'WT06', 'B2': 'WT07', 'B3': 'WT08', 'B4': 'WT09', 'B5': 'WT10', 
          'C1': 'WT11', 'C2': 'WT12', 'C3': 'MUT01', 'C4': 'MUT02', 'C5': 'MUT03', 
          'D1': 'MUT04', 'D2': 'MUT05', 'D3': 'MUT06', 'D4': 'MUT07', 'D5': 'MUT08', 
           'E1': 'MUT09', 'E2': 'MUT10', 'E3': 'MUT11', 'E4': 'MUT12', 'E5': 'MUT13'}

Switched = {'A1': 'MUT01', 'A2': 'MUT02',  'A3': 'MUT03', 'A4': 'MUT04', 'A5': 'MUT05', 
            'B1': 'MUT06', 'B2': 'MUT07', 'B3': 'MUT08',  'B4': 'MUT09', 'B5': 'MUT10', 
            'C1': 'MUT11', 'C2': 'MUT12', 'C3': 'MUT13', 'C4': 'WT01', 'C5': 'WT02', 'D1': 'WT03',
             'D2': 'WT04', 'D3': 'WT05', 'D4': 'WT06', 'D5': 'WT07', 'E1': 'WT08', 
             'E2': 'WT09', 'E3': 'WT10', 'E4': 'WT11', 'E5': 'WT12'}

# define plot settings
colors = ['deep sea blue', 'dark hot pink', 'british racing green', 'blood', 
          'cement','pastel purple','vomit green','golden yellow', 'aqua marine', 'coral']
pal = sns.xkcd_palette(colors)
sns.set(context = 'paper', font_scale = 3)

### Start of Analysis

# Define working directories (variable number of conditions possible)
# NOTE: For performance it is recommended to not analyse more than 
#       4 conditions simultaneously.
cond_num = input('How many different conditions do you have? \n')
data_loc = {}
for i in range(int(cond_num)):
    loc = input('Where is the data for condition ' + str(i+1) + '? \n')
    data_loc[i+1] = loc
#    del loc

# Perform data extraction on all given directories
ans1 = input('Do you want to extract data for all conditions now? (y/n) \n').lower()
if ans1 == 'y':
    print('Extracting data...')
    extr_data = {}
    for i in range(len(data_loc)):
        extr_data['cond'+str(i+1)] = data_extraction(data_loc[i+1])
        
else:
    quit()
# del i, data_loc
          
# possibility to check if number of frames is at least 90% of expected count        
ans2 = input('Do you wish to check for tracking coverage? (y/n) \n').lower()

# checking frame number if desired
if ans2 == 'y':
    frame_num = int(input('How many frames do your tracked videos have? \n'))
    print('Checking for complete tracking...')
    ex_well = check_track(extr_data, frame_num)

    # possibility to exclude data, automatically suggested list of wells is
    # modifiable by user input
    print('Do you wish to exclude these files from analysis? (y/n)')
    print('If you wish to include/exclude additional files enter + or -')
    ans3 = input().lower()
   
    if ans3 == 'y':
        print('Removing badly tracked wells...')
        remove_data(extr_data, ex_well)
    elif ans3 == '-':
        x = 'y'
        while x == 'y':
            new_ex = input('Please enter well-number of files to exclude from analysis: ')
            if len(new_ex) == 2:
                ex_well.append(new_ex)
            else:
                print('It seems you entered something that is not a well number.')
                continue
            print ('Do you wish to exclude further wells? (y/n)')
            x = input().lower()
        print('Removing badly tracked wells...')
        remove_data(extr_data, ex_well)
    elif ans3 == '+':
        x = 'y'
        while x == 'y':
            try:
                ex_well.remove(input('Please enter well-number of files to include despite bad tracking: '))
            except ValueError:
                print('Please add only one well at a time.')
                continue
            x = input('Do you wish to include further wells? (y/n) \n').lower()
        print('Removing badly tracked wells...')
        remove_data(extr_data, ex_well)
    else:
        print('No data will be excluded, keep in mind potential effects on the result.')
        
else:
    print ('Data will not be checked for tracking coverage.')

# replacing NaN-values
print('Any NA-values within the data will be replaced with interpolated values.' )
ans4 = input('Press enter to continue')

if ans4 == '':
    for c in extr_data:
        for e in extr_data[c]:
            extr_data[c][e].interpolate(inplace = True)
            #extr_data[c][e] = extr_data[c][e].ewm(span=5).mean()
else:
    print('Continue analysis without replacing NAs.')
    
# Defining binsize for the frequency extraction
freq_bin = int(input('''Please enter the binsize for which dominant frequencies shall be extracted. 
                     (in seconds) \n'''))*15 #15 frames per second
mean_factor = 900/freq_bin
if ans2 != 'y':
    print ('Please enter the total number of frames of your video.')
    frame_num = int(input())
else:
    print('Previously defined frame number will be used for evaluation.')

# Define body IDs
bps = extr_data['cond1'][list(extr_data['cond1'].keys())[0]].x.columns.to_numpy().tolist()
ids = list(np.arange(len(bps)))
bodypoints = dict(zip(ids, bps))
#del ids, bps

# Specify points to be used for frequency extraction
print('''Please specify the body points for which frequencies shall be extracted,
      by entering their ID numbers.''')
print(bodypoints)
ans8 = list(input())
points = []
for p in ans8:
    try:
        points.append(bodypoints[int(p)])
    except:
        continue
#del ans8
    
print('Python will extract dominant frequency indices within desired time frame. ('+str(freq_bin/15)+'s)')
freq_list = frequencies(extr_data, frame_num, freq_bin, points)
#del freq_bin, points, extr_data

# binning data and calculating means per worm with the specified plate-setup
binsize = int(input('Please enter binsize for plotting in minutes: '))
print('Frequency data will be binned in ' + str(binsize) +'-minute bins.')
hours_tracked = int(input('How many hours were tracked? \n'))
plate_set_up = input('''Please specify the used plate set-up: \n 
                     Type "c" for Common (WT: A1-C2) \n
                     Type  "s" for Switched (WT: C4-E5) \n''').lower()
if plate_set_up == 's':
    binned_data, means = binning(freq_list, binsize, hours_tracked, Switched, mean_factor)
elif plate_set_up == 'c':
    binned_data, means = binning(freq_list, binsize, hours_tracked, Common, mean_factor)
else:
    print('Your input does not fit to a known plate set-up, thus the Common layout will be used')
    binned_data, means = binning(freq_list, binsize, hours_tracked, Common, mean_factor)
#del freq_list

#data plotting
ans5 = 'y'
while ans5 == 'y':
    ans5 = input('Do you wish to plot any data? (y/n) \n').lower()
    if ans5 != 'y':
        break
    print('Enter condition numbers of conditions you want to plot. There are currently '
          + str(len(means.keys())) + ' different conditions.')
    plot_please = list(input())
    plot_this = []
    for x in plot_please:
        try:
            plot_this.append(int(x))
        except:
            continue
    ans6 = input('Do you wish to plot area under the curve (AUC) as well? (y/n) \n').lower()
    plottable, areas = plot_prep(means, plot_this)
    plotting(plottable, areas, plus_auc = ans6)
    
# Statistical analysis for AUC data
ans9 = input('Do you wish to do statistical testing? (y/n) \n').lower()

if ans9 == 'y':
    normality = check_normal(areas)
while ans9 == 'y':
    test_please = []
    test_please.append(input('Enter first condition to test: \n'))
    test_please.append(input('Enter condition to compare to: \n'))
    
    ind = input('Are these conditions independent from one another? (y/n) \n')
    
    result = stat_test(areas, test_please, normality, ind)
    print(result)
    
    ans9 = input('Do you wish to compare more conditions? (y/n) \n').lower()    
    
# Option to save data for later use/analysis
ans7 = input('Do you want to save data for later plotting? (y/n) \n').lower()
if ans7 == 'y':
    path = input('Please enter a file-path, where results shall be saved: \n')
    date = dt.datetime.now()
    date = date.strftime('%Y%m%d')
    output_name = date + '_Undulation_Ratios.csv'
    output_name2 = date + '_AUC_Data.csv'
    output = os.path.join(path, output_name)
    output2 = os.path.join(path, output_name2)
    plottable, areas = plot_prep(means,list(range(1,len(means.keys())+1)))
    plottable.to_csv(output)
    areas.to_csv(output2)
