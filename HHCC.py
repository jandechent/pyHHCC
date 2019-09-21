# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
# pylint: disable=C0303 # trailing whitespace
# pylint: disable=C0103 # snake
""" File, containing the HHCC class """

import glob
import os.path
import logging
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
# from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
# register_matplotlib_converters()

class HHCC:
    """ Can generate various overview plots for the plant and parameters provided from the export of the FlowerCare app by Xiaomi/HHCC.
    
    :param filename: Either directly a filename (without file extention) or a directory,
                         where the csv files are located. In case of a folder,
                         the csv file with the most recent "date modified" is used.
                         On second loading, a pickeld version of the data is loaded.
    :param ignorePickled: By defualt, the pkl files are used, set to True, to do reparse the .csv files.
    :type filename: `str`
    :type ignorePickled: `bool`
    :ivar list_of_plants: a list with the names of all plants
    :ivar minMax: For plotting we need to know the global min and max values per plotted value and per aggregation.
        ["daily","L","sum","amax"] gives you the maximum values that will ever be plotted for plots that
        show daily data for the sum of light.
    :ivar param: A dict for each parameter (E, L, S, T) to define 'color' for the plots and 'label' for the data.
    :ivar df: the actual pandas dataframe, containing the data."""
    def __init__(self, filename, ignorePickled=False):
        self.log = logging.getLogger(__name__)
        self.param = {"E": {'color':"g",
                            'label':"nutrition (ms/cm)",
                            'label_short':"nutr"},
                      "L": {'color':"y",
                            'label':"light (mol)",
                            'label_short':"light"},
                      "S": {'color':"b",
                            'label':"humidity (%)",
                            'label_short':"humid"},
                      "T": {'color':"r",
                            'label':"temperature (°)",
                            'label_short':"temp"}}
        if os.path.isdir(filename):
            self.log.info("finding .csv with latest creation date from folder: %s", filename)
            list_of_files = glob.glob(filename+'*.csv') # * means all if need specific format then *.csv
            filename = max(list_of_files, key=os.path.getmtime)

        self.df = None
        if os.path.exists(filename+".pkl") & (not ignorePickled):
            self.log.info("loading pkl version of: %s", filename)
            try:
                self.df = pd.read_pickle(filename + ".pkl")
            except Exception as ex:
                self.log.warning("loading failed, attemting to read .csv file:")
                if self.log.level == logging.DEBUG:
                    raise ex

        if self.df is None:
            self.log.info("loading: %s", filename)
            self.__load(filename)
            self.__delete_sensor_fails()
            self.__convert_units()
            self.df = self.df.sort_values('time', ascending=False)
            self.df.to_pickle(filename+".pkl")
        self.list_of_plants = self.df.plant.unique().tolist()
        self.__rolling_mean("none","1h","24h","48h","72h")
        self.__aggregate_daily()
        self.__make_min_max()
        self.__consistency_check()

    def __make_min_max(self):
        """Find the global min and max values for the four parameter, accross all plants and all times."""
        self.minMax = self.df.pivot_table(values=["L", "T", "E", "S"], index=['aggSpan', 'aggFunc'], aggfunc=[np.min, np.max])
        self.tmp=self.minMax.copy()
        self.minMax = self.minMax.stack().stack()
        self.minMax = self.minMax.swaplevel(1, 2)

    def __delete_sensor_fails(self):
        """ Deletes data points, where there was a sensor failure. This function acts inplace on :attr:`HHCC.df`."""
        self.df = self.df[self.df["E"] < 2500]
        self.df = self.df[self.df["L"] < 10000]
        self.df = self.df[self.df["S"] < 100]
        self.df = self.df[self.df["T"] < 100]

    def __convert_units(self):
        """Divide light and conductivity by 1000. This function acts inplace on :attr:`HHCC.df`."""
        self.df["L"] = self.df["L"]/1000
        self.df["E"] = self.df["E"]/1000

    def __load(self, filepath):
        """ Loads the data of the passed in filename

        :param filepath: full path + filename, including file extension
        :type filepath: `str`"""
        self.df = pd.DataFrame()
        with open(filepath, encoding='utf16') as fp:
            line = fp.readline()
            line = line
            cnt = 1
            while line:
                if (line.find("Flower Care")) >= 0:
                    mac = line[13:-2]
                    raw_dates = fp.readline()
                    cnt += 1
                    dates = raw_dates.split("\t")
                    dates = list(filter(None, dates))
                    name = dates.pop(0)
                    raw_params = fp.readline()
                    params = raw_params.split("\t")
                    params = params[1:-1]
                    dates = [dates[(i)//4] for i in range((len(dates)-1)*4)]
                    for _ in range(24):
                        raw_line = fp.readline()
                        cnt += 1
                        value_line = raw_line.split("\t")
                        value_line = value_line[0:-1]
                        hour = value_line.pop(0)
                        hour = hour[1:-1]
                        df_loop = pd.DataFrame([dates, params, value_line], index=['date', 'parameter', 'value']).T
                        if hour == "24:00":
                            df_loop['hour'] = "00:00"
                            df_loop['time'] = pd.to_datetime(df_loop["date"]+" "+df_loop["hour"])
                            df_loop['time'] = df_loop['time']+ pd.DateOffset(days=1)
                        else:
                            df_loop['hour'] = hour
                            df_loop['time'] = pd.to_datetime(df_loop["date"]+" "+df_loop["hour"])
                        df_loop = df_loop.drop(['date', 'hour'], axis=1)
                        df_loop['value'] = pd.to_numeric(df_loop['value'], errors='coerce')
                        df_loop = df_loop[np.isnan(df_loop['value']) == False]
                        df_loop = df_loop.pivot(values="value", index="time", columns="parameter")
                        df_loop = df_loop.reset_index()
                        df_loop['plant'] = name
                        df_loop['mac'] = mac
                        df_loop["aggFunc"] = "none"
                        df_loop["aggSpan"] = "1h"
                        self.df = self.df.append(df_loop, ignore_index=True)
                line = fp.readline()
                cnt += 1
        self.__mem_squeeze(self.df)

    @staticmethod
    def __flatten(li):
        """ flattens a nested list """
        return sum(([x] if not isinstance(x, list) else HHCC.__flatten(x) for x in li), [])

    @staticmethod
    def __mem_squeeze(df):
        """ Applies optimizations to the passed dataframe to use 'pd.Categorial' and to downcast the floats, where possible. """
        df['mac'] = pd.Categorical(df.mac)
        df['plant'] = pd.Categorical(df.plant)
        df['plant'] = pd.Categorical(df.plant)
        df['aggFunc'] = pd.Categorical(df.aggFunc)
        df['aggSpan'] = pd.Categorical(df.aggSpan)
        df["T"] = pd.to_numeric(df["T"], downcast='float')
        df["E"] = pd.to_numeric(df["E"], downcast='float')
        df["L"] = pd.to_numeric(df["L"], downcast='float')
        df["S"] = pd.to_numeric(df["S"], downcast='float')
        #hc.df.melt(id_vars=['plant','mac','time','aggFunc','aggSpan'],value_vars=["T","S","L","E"],var_name="parameter")

    def __consistency_check(self):
        """ Checks :attr:`HHCC.df` for consistency and raises warning messages for the following case: The sensor can only store data for +-30(?) days. Therefore, warn the user to sync soon enough (15 days). """
        warnTimeLimit = "15 days"
        self.df["no update for"] = pd.to_timedelta(dt.datetime.now()-self.df["time"])
        noUpSinceTable = self.df.pivot_table(values='no update for', aggfunc=np.min, index="plant")
        noUpSinceBool = self.df.pivot_table(values='no update for', aggfunc=np.min, index="plant") > pd.to_timedelta(warnTimeLimit)
        noUpSinceBoolSum = noUpSinceBool.agg("sum").values[0]
        if noUpSinceBoolSum > 0:
            self.log.warning("at least one plant was not updated for %s since today:\n %s", warnTimeLimit,
                             noUpSinceTable.sort_values(by=['no update for'], ascending=False).astype("timedelta64[D]").to_string())
        self.df.drop(["no update for"], axis=1, inplace=True)

    def __aggregate_daily(self):
        """ The raw data are provided on an 1h basis. This function calculates min, max, mean and sum
        for each parameter per day. This function acts inplace on :attr:`HHCC.df`."""
        df = self.df[(self.df["aggFunc"] == "none") & (self.df["aggSpan"] == "1h") ].copy()
        df['time'] = pd.to_datetime(df['time'].dt.date)+pd.to_timedelta("12h")
        self.__aggregate_daily_helper(df, np.sum, "sum", "daily")
        self.__aggregate_daily_helper(df, np.min, "min", "daily")
        self.__aggregate_daily_helper(df, np.max, "max", "daily")
        self.__aggregate_daily_helper(df, np.mean, "mean", "daily")
        self.df.reset_index(drop=True, inplace=True)
        self.__mem_squeeze(self.df)
        self.df = self.df.sort_values('time', ascending=False)

    def __aggregate_daily_helper(self, df, aggFunc, aggFunc_label, aggSpan):
        dd = df.pivot_table(values=["L", "T", "E", "S"], index=['time', 'plant', 'mac'], aggfunc=aggFunc)
        dd.reset_index(inplace=True)
        dd["aggFunc"] = aggFunc_label
        dd["aggSpan"] = aggSpan
        self.df = self.df.append(dd, sort=False)

    def rolling_mean(self, wnds, aggFunc, aggSpan):
        df=self.df[(self.df["aggFunc"] == aggFunc) & (self.df["aggSpan"] == aggSpan)]
        df=df.drop("aggFunc",axis=1)
        df=df.drop("aggSpan",axis=1)
        df=df.set_index(["plant","mac","time"]).sort_index()
        df_toappend = pd.DataFrame()
        if not isinstance(wnds, list):
            wnds = [wnds]
        for wnd in wnds:
            if wnd in self.df.aggSpan.unique():
                self.log.warning("aggSpan %s already exists, skipping.",wnd)
            else:
                for index, sub_df in df.groupby(['plant', 'mac']):
                    sub_df = sub_df.reset_index(['plant', 'mac'],drop=True)
                    sub_df=sub_df.rolling(wnd).mean()
                    sub_df["plant"] = index[0]
                    sub_df["mac"] = index[1]
                    sub_df["aggFunc"] = "mean" 
                    sub_df["aggSpan"] = wnd
                    df_toappend=df_toappend.append(sub_df.reset_index())
        self.df = self.df.append(df_toappend,sort=False)
        self.__mem_squeeze(self.df)
        self.df = self.df.sort_values('time', ascending=False)
        self.df = self.df.reset_index(drop=True)
        self.__make_min_max()
        
    def rename_plants(self, rules=None):
        """ Renames the plants based on the passed dict.

        :param rules: a dict with the original and new names. If nothing is passed, the existing names are cropped after the first round bracket.
        :type rules: `dict`, optional"""
        if rules is None:
            ren = dict()
            for plant in self.list_of_plants:
                num = plant.find("(")
                ren.update({plant: plant[0:num-1]})
            self.df["plant"].cat.rename_categories(ren, inplace=True)
        else:
            self.df["plant"].cat.rename_categories(rules, inplace=True)
        self.list_of_plants = self.df.plant.unique().tolist()

    def plot_save(self,name, **kwargs):
        """ Stores the current figure.
        
        :param store: `True` to store the plot. Defaults to `False`. 
        :type store: `bool`
        :param outputdir: The output directory for the plots, which can be generated. Defautls to "plots/"
        :type outputdir: `str`, optional
        :param dpi: The dpi of the plot, defaults to 300
        :type dpi: `int`, optional
        :param override_name: Overwrites the default naming with this name. 
        :type override_name: `str`, optional"""
        if kwargs.get('store', False):
            name = kwargs.get('override_name', name) 
            outputdir = kwargs.get('outputdir', "plots/") 
            dpi = kwargs.get('dpi', 300) 
            plt.gcf().savefig(outputdir + name, dpi=dpi)

    def plot_onePlant_oneParam(self, ax, plant, param, **kwargs):
        """ Plots dta from one plant and the passed parameter. 
        
        :param ax: The axis to draw the plot to.
        :type ax: `plt.ax`
        :param plant: Name of the plant (for names, check :attr:`HHCC.list_of_plants`)
        :type plant: `str`
        :param param: Which of the four parameter to plot: T, E, S, L.
        :type param: `str`

        When this function is called as part of :meth:`HHCC.plot_onePlant`, :meth:`HHCC.plot_onePlant_batch` or :meth:`HHCC.plot_allPlants`, the following optional parameters can be set and pass though till this function. 

        :param light_as_integral: `True` to show the light as integral over one day, in this case, aggFunc and aggSpan are overwritten locally. Defaults to `false`.
        :type light_as_integral: `bool`, optional, passthrough
        :param time_delta: Defines the timespan of the plots from today backwards. The passed argument is processed using `pd.to_timedelta`, defaults to 90 days.
        :type time_delta: `str`, optional
        :param ylims_global: `True` to scale the y axis per parameter equally over all plants. `False` to scale each plot individually. Defaults to `True`.
        :type ylims_global: `bool`, optional
        :param smoothingWnd: optional, the window with for smoothing. Default for parameters E, S, T is 48h. L is not soothed by default. For individual adjustments, set `smoothingWnd_E`, `smoothingWnd_S`, `smoothingWnd_L` and/or `smoothingWnd_T`
        :param alphaOriginal: optional, 0.3 by default to suplress the visibility of unsmoothed data.
        :param alphaSmoothed: optional, 1.0 by default to highlight the plot of smoothed data.
        :type alphaOriginal: `float`, optional
        :type alphaSmoothed: `float`, optional
        :type smoothingWnd: `float`, optional
        
        The following parameters are typically pre set by the superseeding functions above. 
        
        :param aggFunc:
        :type aggFunc: `str`, optional
        :param aggSpan:
        :type aggSpan: `str`, optional
        :param label_short: `True` to shorten the labels. `False` to use the long labels. Defaults to `False`.
        :type label_short: `bool`, optional
        :param hide_ticks: `True` to all x and y labels and ticks from the plot. `False` to show. Defaults to `False`. Can be refined using `hide_xTicks` or `hide_yTicks`.
        :type hide_ticks: `bool`, optional
        :param time_labels: "month" to show month on the major ticks and days as minor ticks.
        :type time_labels: `str`, optional"""
        df = self.df
        aggFunc = kwargs.get('aggFunc', "none")
        aggSpan = kwargs.get('aggSpan', "1h")

        if kwargs.get('light_as_integral', False) & (param == 'L'):
            aggFunc = "sum"
        
        alphaOriginal = kwargs.get('alphaOriginal', 1)
        alphaSmoothed = kwargs.get('alphaSmoothed', 1)
        time_delta = kwargs.get('time_delta', '90days')
        startTime = (pd.to_datetime(dt.datetime.now().date()) - pd.to_timedelta(time_delta))+pd.to_timedelta("24h")
        endTime = pd.to_datetime(dt.datetime.now().date())+pd.to_timedelta("24h")
        cTime = startTime <= df["time"]
        cPlant = df["plant"] == plant
        cAggFunc = df["aggFunc"] == aggFunc
        cAggSpan = df["aggSpan"] == aggSpan

        df = df[cPlant&cTime&cAggFunc&cAggSpan][["time", param]]
        df = df.set_index("time")

        smoothingWnd = {"E": kwargs.get('smoothingWnd_E', 48 if kwargs.get('smoothingWnd', "default") == "default" else kwargs.get('smoothingWnd')),
                        "S": kwargs.get('smoothingWnd_S', 48 if kwargs.get('smoothingWnd', "default") == "default" else kwargs.get('smoothingWnd')),
                        "T": kwargs.get('smoothingWnd_T', 48 if kwargs.get('smoothingWnd', "default") == "default" else kwargs.get('smoothingWnd')),
                        "L": kwargs.get('smoothingWnd_L', 1 if kwargs.get('smoothingWnd', "default") == "default" else kwargs.get('smoothingWnd'))}
        ax.plot(df, color=self.param[param]['color'], alpha=alphaOriginal) #tmp.plot would not work, because sharex somehow messes things up and some data don't show on some graph. Very stragen, but this fixes it.
#        if param == "E":
#            df = df.rolling(smoothingWnd["E"], center=True).median()
#        if param == "S":
#            df = df.rolling(smoothingWnd["S"], center=True).mean()
#        if param == "T":
#            df = df.rolling(smoothingWnd["T"], center=True).mean()
#        if param == "L":
#            df = df.rolling(smoothingWnd["L"], center=True).mean()
#        ax.plot(df, color=self.param[param]['color'], alpha=alphaSmoothed)

        ax.set_xlim(startTime, endTime)
        if kwargs.get('ylims_global', "True"):
            ax.set_ylim(0, self.minMax[aggSpan, param, aggFunc, "amax"])

        ax.set_xlabel("")
        ax.set_ylabel(self.param[param]["label" if not kwargs.get('label_short', False) else "label_short"])

        years = mdates.YearLocator()   # every year
        months = mdates.MonthLocator()  # every month
        days = mdates.DayLocator()  # every month
        hours = mdates.HourLocator()  # every month
        years_fmt = mdates.DateFormatter('%Y')
        months_fmt = mdates.DateFormatter('%Y-%m')
        days_fmt = mdates.DateFormatter('%Y-%m-%d')

        time_labels = kwargs.get('time_labels', 'month')
        if time_labels == "year":
            ax.xaxis.set_major_locator(years)
            ax.xaxis.set_major_formatter(years_fmt)
            ax.xaxis.set_minor_locator(months)
            ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        elif time_labels == "month":
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(months_fmt)
            ax.xaxis.set_minor_locator(days)
            ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        elif time_labels == "day":
            ax.xaxis.set_major_locator(days)
            ax.xaxis.set_major_formatter(days_fmt)
            ax.xaxis.set_minor_locator(hours)
            ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        else:
            self.log.error("unknown parameter for 'time_labels' ")
        
        if kwargs.get('hide_xTicks', False) | kwargs.get('hide_ticks', False):
            ax.get_xaxis().set_ticks([])
            ax.get_xaxis().set_ticklabels([])
        if kwargs.get('hide_yTicks', False) | kwargs.get('hide_ticks', False):
            ax.set_ylabel("")
            ax.get_yaxis().set_ticks([])
            ax.get_yaxis().set_ticklabels([])

    def plot_onePlant(self, plant=None, **kwargs):
        """ Generates one plot of the four parameters light, temperature, nutrition and light over time. For further available settings, see :meth:`HHCC.plot_onePlant_oneParam` - but some might be defined along the call stack.

        :param plant: The plant that shall be plotted, defaults to the first plant. 
        :type plant: `str`, optional
        :param store: `True` to store the plot. Defaults to `False`. See :meth:`HHCC.plot_save` for further details.
        :type store: `bool`, optional
        :param landscape: `True` to provide a 2x2 plot. `False` to plot the parameters in one row. Defaults to `True`.
        :type landscape: `bool`, optional"""        
        if plant is None:
            plant = self.list_of_plants[0]
        if kwargs.get('landscape', False):
            fig = plt.figure(num=plant, figsize=[10, 3])
            ax1 = fig.add_subplot(141)
            ax2 = fig.add_subplot(142, sharex=ax1)
            ax3 = fig.add_subplot(143, sharex=ax1)
            ax4 = fig.add_subplot(144, sharex=ax1)
        else:
            fig = plt.figure(num=plant, figsize=[10, 6])
            ax1 = fig.add_subplot(221)
            ax2 = fig.add_subplot(222, sharex=ax1)
            ax3 = fig.add_subplot(223, sharex=ax1)
            ax4 = fig.add_subplot(224, sharex=ax1)
        self.plot_onePlant_oneParam(ax1, plant, "E", **kwargs)
        self.plot_onePlant_oneParam(ax2, plant, "S", **kwargs)
        self.plot_onePlant_oneParam(ax3, plant, "L", **kwargs)
        self.plot_onePlant_oneParam(ax4, plant, "T", **kwargs)
        fig.autofmt_xdate()
        fig.align_ylabels()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.suptitle(plant, fontsize=14)
        self.plot_save("Health of " + plant, **kwargs)

    def plot_onePlant_batch(self, **kwargs):
        """ Calls :meth:`HHCC.plot_onePlant` for all available plants. For further available settings, see :meth:`HHCC.plot_onePlant_oneParam` - but some might be defined along the call stack.
        
        :param store: `True` to store the plot. Defaults to `False`. See :meth:`HHCC.plot_save` for further details.
        :type store: `bool`, optional"""
        for plant in self.list_of_plants:
            self.plot_onePlant(plant, **kwargs)

    def plot_allPlants(self, **kwargs):
        """ Generates one comprehensive plot for all plants and the four parameters light, temperature, nutrition and light over time. For further available settings, see :meth:`HHCC.plot_onePlant_oneParam` - but some might be defined along the call stack.

        :param store: `True` to store the plot. Defaults to `False`. See :meth:`HHCC.plot_save` for further details.
        :type store: `bool`, optional
        :param landscape: `True` to plot the plants as colums and the params as columns. `False` to plot transposed. Defaults to `True`.
        :type landscape: `bool`, optional""" 
        if kwargs.get('landscape', True):
            fig, axs = plt.subplots(4, len(self.list_of_plants), sharex=True, figsize=(10, len(self.list_of_plants)))
            for (i, plant) in enumerate(self.list_of_plants):
                self.plot_onePlant_oneParam(axs[0, i], plant, "E", **kwargs, hide_ticks=bool(i), label_short=True)
                self.plot_onePlant_oneParam(axs[1, i], plant, "S", **kwargs, hide_ticks=bool(i), label_short=True)
                self.plot_onePlant_oneParam(axs[2, i], plant, "L", **kwargs, hide_ticks=bool(i), label_short=True)
                self.plot_onePlant_oneParam(axs[3, i], plant, "T", **kwargs, hide_xTicks=False, hide_yTicks=bool(i), label_short=True)
                axs[0, i].title.set_text(plant)
            fig.autofmt_xdate()
        else:
            fig, axs = plt.subplots(len(self.list_of_plants), 4, sharex=True, figsize=(10, 2.5*len(self.list_of_plants)))
            for (i, plant) in enumerate(self.list_of_plants):
                self.plot_onePlant_oneParam(axs[i, 0], plant, "E", **kwargs, hide_yTicks=True)
                self.plot_onePlant_oneParam(axs[i, 1], plant, "S", **kwargs, hide_yTicks=True)                
                self.plot_onePlant_oneParam(axs[i, 2], plant, "L", **kwargs, hide_yTicks=True)                
                self.plot_onePlant_oneParam(axs[i, 3], plant, "T", **kwargs, hide_yTicks=True)        
                axs[i, 0].set_ylabel(plant)
            axs[0, 0].title.set_text(self.param["E"]["label"])
            axs[0, 1].title.set_text(self.param["S"]["label"])
            axs[0, 2].title.set_text(self.param["L"]["label"])
            axs[0, 3].title.set_text(self.param["T"]["label"])
            fig.autofmt_xdate()
        plt.tight_layout(rect=[0, 0, 1, 1])
        plt.subplots_adjust(hspace=.001)
        plt.subplots_adjust(wspace=.001)
        
        HHCC.plot_save("Overview", **kwargs)               
