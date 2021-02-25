import os
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches

def set_grid(ax):
    ax.grid(
        which='major',
        axis='x', 
        linewidth=0.75, 
        linestyle='-', 
        color='0.75'
    )
    ax.grid(
        which='major', 
        axis='y', 
        linewidth=0.75, 
        linestyle='-', 
        color='0.75'
    )

def plot_weekly(dframe, target_dir=None):
    fig, ax = plt.subplots(figsize=(12.8, 9.6))
    fig.suptitle('Reported weekly COVID-19 data Netherlands')
    df_week = dframe.drop_duplicates(subset='week_number')
    weeks = df_week.week_number.astype('int').unique()
    width = 0.6
    
    p1 = ax.bar(weeks,
        df_week.infection_week,
        width=width,
        label='Reported infections')
    
    p2 = ax.bar(weeks,
        df_week.hospital_week,
        width=width,
        bottom=df_week.infection_week,
        label='Reported hospital admissions')

    p3 = ax.bar(weeks,
        df_week.dead_week,
        width=width,
        bottom=df_week.infection_week + df_week.hospital_week,
        label='Reported deaths')

    # Set limits on y and x axis
    ax.set_ylim(0, df_week.infection_week.max() + 2000)
    ldate = df_week.week_number.min() - 1
    hdate = df_week.week_number.max() + 1
    ax.set_xbound(ldate, hdate)
    # Set ticker spacing
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2000))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

    set_grid(ax)
    # Add source annotation
    ax.annotate(f'Source: RIVM https://data.rivm.nl/covid-19/',
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')

    plt.legend(loc='upper left', frameon=False)
    plt.xlabel('Week')
    plt.ylabel('Reported amount')

    if target_dir:
        fp = os.path.join(target_dir, 'weeklycombined.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def plot_current_ic_zkh(dframe, target_dir=None):

    df_current = dframe[dframe['week_number'] > 7]
    fig = plt.figure(figsize=(13.8, 11.6))
    width = 0.5
    fig.tight_layout()
    ax = plt.subplot(111)
    fig.suptitle('Total reported COVID patients Hospital')
    ax.set_ylim(0, (df_current.ZKH_current.max() + 
        df_current.IC_current.max()) + 50)
    ldate = df_current.date.min() - timedelta(days=1)
    hdate = df_current.date.max() + timedelta(days=1)
    ax.set_xlim(ldate, hdate)
    p1 = ax.bar(df_current.date, df_current.ZKH_current,
        width, label='Reported COVID patients nursing ward')
    p2 = ax.bar(df_current.date, df_current.IC_current, 
        width, bottom=df_current.ZKH_current, label='Reported COVID patients IC')

    set_grid(ax)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(250))
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    plt.legend(loc='upper right', frameon=False)
    plt.xlabel('Date')
    plt.ylabel('Reported amount')

    # Add source annotation
    ax.annotate(('Sources:' \
        'https://stichting-nice.nl/covid-19/public/intake-count/' \
        '\n https://stichting-nice.nl/covid-19/public/zkh/intake-count/'),
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')

    if target_dir:
        fp = os.path.join(target_dir, 'currenticzkh.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def subplot_daily_infections(dframe, target_dir=None):

    rolling_avg_inf = dframe.infection_day.rolling(7).mean()
    rolling_avg_hos = dframe.hospital_day.rolling(7).mean()
    rolling_avg_death = dframe.dead_day.rolling(7).mean()

    fig = plt.figure(figsize=(15, 11.2))
    fig.tight_layout()
    gs1 = fig.add_gridspec(nrows=3, ncols=2)
    fig.suptitle('Daily reported COVID-19 data Netherlands')

    fig_ax1 = fig.add_subplot(gs1[:-1, :])
    fig_ax1.set_title('Reported infections', fontsize=10)
    fig_ax1.bar(dframe.date, 
        dframe.infection_day,
        width=0.6)
        # label='Daily infections')
    fig_ax1.plot(dframe.date, 
        rolling_avg_inf, 
        color='purple',
        linewidth=1,
        linestyle='-',
        label='7-day rolling average') 
    fig_ax1.legend(loc='upper left', frameon=False)
    fig_ax1.set_ylim(0, dframe.infection_day.max() + 500)
    fig_ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    fig_ax1.yaxis.set_major_locator(ticker.MultipleLocator(500))

    fig_ax2 = fig.add_subplot(gs1[-1, :-1])
    fig_ax2.set_title('Reported hospital Admissions', fontsize=8)
    fig_ax2.bar(dframe.date, 
        dframe.hospital_day,
        width=1,
        label='Reported hospital admissions')
    fig_ax2.plot(dframe.date, 
        rolling_avg_hos, 
        color='purple',
        linewidth=1,
        linestyle='-',
        label='7-day rolling average') 
    fig_ax2.set_ylim(0, dframe.hospital_day.max() + 100)
    fig_ax2.xaxis.set_major_locator(mdates.DayLocator(interval=14))
    fig_ax2.yaxis.set_major_locator(ticker.MultipleLocator(100)) 

    fig_ax3 = fig.add_subplot(gs1[-1, -1])
    fig_ax3.set_title('Reported deaths', fontsize=8)
    fig_ax3.bar(dframe.date, 
        dframe.dead_day,
        width=1,
        label='Reported deaths')
    fig_ax3.plot(dframe.date, 
        rolling_avg_death, 
        color='purple',
        linewidth=1,
        linestyle='-',
        label='7-day rolling average') 
    fig_ax3.set_ylim(0, dframe.dead_day.max() + 50)
    fig_ax3.xaxis.set_major_locator(mdates.DayLocator(interval=14))
    fig_ax3.yaxis.set_major_locator(ticker.MultipleLocator(50)) 

    ldate = dframe.date.min() - timedelta(days=3)
    hdate = dframe.date.max() + timedelta(days=3)
    for f in [fig_ax1, fig_ax2, fig_ax3]:
        set_grid(f)
        f.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
        f.set_xbound(ldate, hdate)
        plt.setp(f.get_xticklabels(), 
            rotation=45, 
            ha="right", 
            fontsize=8)
        plt.setp(f.get_yticklabels(),  
            fontsize=8)


    fig_ax1.annotate(f'Source: RIVM https://data.rivm.nl/covid-19/',
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')

    fig.subplots_adjust(left=None, bottom=None, right=None, top=0.90,
        wspace=0.1, hspace=0.6)
    if target_dir:
        fp = os.path.join(target_dir, 'dailycombined.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def subplot_weekly(dframe, target_dir=None):
    df_week = dframe.drop_duplicates(subset='week_number')
    weeks = df_week.week_number.astype('int').unique()
    width = 0.6
    fig = plt.figure(figsize=(12.8, 9.6))
    fig.tight_layout()
    gs1 = fig.add_gridspec(nrows=2, ncols=2)
    fig.suptitle('Weekly reported COVID-19 data Netherlands')

    fig_ax1 = fig.add_subplot(gs1[0, :])
    fig_ax1.set_title('Reported infections', fontsize=10)
    fig_ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
    fig_ax1.yaxis.set_major_locator(ticker.MultipleLocator(5000))
    fig_ax1.set_ylim(0, df_week.infection_week.max() + 20000)
    p1 = fig_ax1.bar(weeks, 
        df_week.infection_week,
        width=width,
        label='Reported weekly infections')
    fig_ax1.legend(loc='upper right', frameon=False)


    for x,y in zip(weeks, df_week.infection_week):
        fig_ax1.text(x, y+0.05, int(y),
            ha='center',
            va= 'bottom', 
            fontsize=8,
            alpha=0.8,
            color='black')

    fig_ax2 = fig.add_subplot(gs1[1 , : ])
    fig_ax2.set_title('Reported hospital admissions & deaths', fontsize=10)
    fig_ax2.xaxis.set_major_locator(ticker.MultipleLocator(1))
    fig_ax2.yaxis.set_major_locator(ticker.MultipleLocator(500))
    p2 = fig_ax2.bar(weeks,
        df_week.hospital_week,
        width=width,
        label='Reported hospital admissions')

    p3 = fig_ax2.bar(weeks,
        df_week.dead_week,
        width=width,
        bottom=df_week.hospital_week,
        label='Reported deaths')
    fig_ax2.legend(loc='upper right', frameon=False)
    
    ldate = df_week.week_number.min() - 1
    hdate = df_week.week_number.max() + 1
    
    for f in [fig_ax1, fig_ax2]:
        set_grid(f)
        f.set_xbound(ldate, hdate)
        plt.setp(f.get_yticklabels(),  
            fontsize=8)

    fig_ax1.annotate(f'Source: RIVM https://data.rivm.nl/covid-19/',
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')
    
    plt.xlabel('Week')
   
    if target_dir:
        fp = os.path.join(target_dir, 'weeklycombined2.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def plot_weekly_infections(dframe, target_dir=None):
    fig = plt.figure(figsize=(12.8, 9.6))
    fig.tight_layout()
    fig.suptitle('Reported infections by week')
    ax = plt.subplot(111)
    ax.bar(dframe["week_number"].astype('int').unique(),
        dframe["infection_week"].unique(),
        edgecolor='white',
        width=0.6,
        label='Weekly reported infections')

    for x,y in zip(dframe.week_number, dframe.infection_week):
        plt.text(x, y+0.05, int(y),
            ha='center',
            va= 'bottom', 
            fontsize=8,
            alpha=0.4,
            color='gray')

    # Set limits on y and x axis
    ax.set_ylim(0, dframe.infection_week.max() + 2000)
    ldate = dframe.week_number.min() - 1
    hdate = dframe.week_number.max() + 1
    ax.set_xbound(ldate, hdate)
    # Set ticker spacing
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2500))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.legend(loc='upper left', frameon=False)
    plt.xlabel('Week')
    plt.ylabel('Reported infections')

    set_grid(ax)

    # Add source annotation
    ax.annotate(f'Source: RIVM  https://data.rivm.nl/covid-19/',
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')

    if target_dir:
        fp = os.path.join(target_dir, 'weeklyinfections.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def plot_daily_infections(dframe, target_dir=None):
    rolling_avg = dframe.infection_day.rolling(7).mean()
    
    fig = plt.figure(figsize=(12.8, 9.6))
    fig.tight_layout()
    ax = plt.subplot(111)
    fig.suptitle('Reported daily Infections over time')
    # Plot the daily infections
    ax.bar(dframe.date, 
        dframe.infection_day,
        width=0.5,
        label='Reported infections')

    # Plot the rolling average
    ax.plot(dframe.date, 
        rolling_avg, 
        color='purple',
        linewidth=1,
        linestyle='-',
        label='7-day rolling average')

    # Set limits on y and x axis
    ax.set_ylim(0, dframe.infection_day.max() + 500)
    ldate = dframe.date.min()
    hdate = dframe.date.max() + timedelta(days=1)
    ax.set_xbound(ldate, hdate)

    set_grid(ax)

    plt.gcf().autofmt_xdate()
    plt.xticks(fontsize=8)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(500))
    plt.legend(loc='upper left', frameon=False)
    plt.xlabel('Date')
    plt.ylabel('Reported infections')

    # Add source annotation
    ax.annotate(f'Source: RIVM https://data.rivm.nl/covid-19/',
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')

    if target_dir:
        fp = os.path.join(target_dir, 'dailyinfections.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def plot_testing_data(dframe, rapport_name, target_dir=None):

    fig = plt.figure(figsize=(12.8, 9.6))
    fig.tight_layout()
    ax = plt.subplot(111)
    fig.suptitle('Weekly reported test results GGD')
    # Set limits on y and x axis
    ldate = dframe.week_number.min() - 1
    hdate = dframe.week_number.max() + 1
    ax.set_xbound(ldate, hdate)
    ax.set_ylim(0, dframe.aantal_testen.max() + 100000)
    # Set ticker spacing
    ax.yaxis.set_major_locator(ticker.MultipleLocator(25000))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    # Plot data
    ax.bar(dframe.week_number, dframe.aantal_testen, 
        0.49, label='Tests', align='center')
    ax.bar(dframe.week_number, dframe.aantal_positief, 
        0.5, label='Positive', align='center')

    # Add percentages 
    for x,y,a in zip(dframe.week_number, dframe.perentage_positief, 
        dframe.aantal_testen):
        ax.text(x, a+0.2, f'{float(y)}%',
            ha='center',
            va= 'bottom', 
            fontsize=8,
            alpha=0.8,
            color='black')
    # Grid formatting
    set_grid(ax)

    # Add source annotation
    ax.annotate(f'Source: RIVM {rapport_name} ',
        xy=(0.5, 0), xytext=(0, 10),
        xycoords=('axes fraction', 'figure fraction'),
        textcoords='offset points',
        size=8, ha='center', va='bottom')


    plt.legend(loc='upper right', frameon=False)
    plt.xlabel('Week')
    plt.ylabel('Reported amount')

    if target_dir:
        fp = os.path.join(target_dir, 'testingweekly2.png')
        plt.savefig(fp)
    else:
        plt.show()
        plt.close()

def plot_and_save_all(dframe, plot_target_dir=None):
    ''' Creates all the above plots and saves the resulting
    figures into the plot directory. '''
    print('Starting plots.')
    plot_weekly(dframe, target_dir=plot_target_dir)
    plot_current_ic_zkh(dframe, target_dir=plot_target_dir)
    subplot_daily_infections(dframe, target_dir=plot_target_dir)
    subplot_weekly(dframe, target_dir=plot_target_dir)
    plot_weekly_infections(dframe, target_dir=plot_target_dir)
    plot_daily_infections(dframe, target_dir=plot_target_dir) 