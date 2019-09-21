<!-- HHCC.py documentation master file, created by
sphinx-quickstart on Wed Aug 28 13:41:42 2019.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive. -->
# Documentation


#### class pyHHCC.pyHHCC(filename, ignorePickled=False)
Can generate various overview plots for the plant and parameters provided from the export of the FlowerCare app by Xiaomi/HHCC.


* **Parameters**

    * **filename** (str) – Either directly a filename (without file extention) or a directory,
      where the csv files are located. In case of a folder,
      the csv file with the most recent “date modified” is used.
      On second loading, a pickeld version of the data is loaded.

    * **ignorePickled** (bool) – By defualt, the pkl files are used, set to True, to do reparse the .csv files.



* **Variables**

    * **list_of_plants** – a list with the names of all plants

    * **minMax** – For plotting we need to know the global min and max values per plotted value and per aggregation.
      [“daily”,”L”,”sum”,”amax”] gives you the maximum values that will ever be plotted for plots that
      show daily data for the sum of light.

    * **param** – A dict for each parameter (E, L, S, T) to define ‘color’ for the plots and ‘label’ for the data.

    * **df** – the actual pandas dataframe, containing the data.



#### plot_allPlants(\*\*kwargs)
Generates one comprehensive plot for all plants and the four parameters light, temperature, nutrition and light over time. For further available settings, see `pyHHCC.plot_onePlant_oneParam()` - but some might be defined along the call stack.


* **Parameters**

    * **store** (bool, optional) – True to store the plot. Defaults to False. See `pyHHCC.plot_save()` for further details.

    * **landscape** (bool, optional) – True to plot the plants as colums and the params as columns. False to plot transposed. Defaults to True.



#### plot_onePlant(plant=None, \*\*kwargs)
Generates one plot of the four parameters light, temperature, nutrition and light over time. For further available settings, see `pyHHCC.plot_onePlant_oneParam()` - but some might be defined along the call stack.


* **Parameters**

    * **plant** (str, optional) – The plant that shall be plotted, defaults to the first plant.

    * **store** (bool, optional) – True to store the plot. Defaults to False. See `pyHHCC.plot_save()` for further details.

    * **landscape** (bool, optional) – True to provide a 2x2 plot. False to plot the parameters in one row. Defaults to True.



#### plot_onePlant_batch(\*\*kwargs)
Calls `pyHHCC.plot_onePlant()` for all available plants. For further available settings, see `pyHHCC.plot_onePlant_oneParam()` - but some might be defined along the call stack.


* **Parameters**

    **store** (bool, optional) – True to store the plot. Defaults to False. See `pyHHCC.plot_save()` for further details.



#### plot_onePlant_oneParam(ax, plant, param, \*\*kwargs)
Plots dta from one plant and the passed parameter.


* **Parameters**

    * **ax** (plt.ax) – The axis to draw the plot to.

    * **plant** (str) – Name of the plant (for names, check `pyHHCC.list_of_plants`)

    * **param** (str) – Which of the four parameter to plot: T, E, S, L.


When this function is called as part of `pyHHCC.plot_onePlant()`, `pyHHCC.plot_onePlant_batch()` or `pyHHCC.plot_allPlants()`, the following optional parameters can be set and pass though till this function.


* **Parameters**

    * **light_as_integral** (bool, optional, passthrough) – True to show the light as integral over one day, in this case, aggFunc and aggSpan are overwritten locally. Defaults to false.

    * **time_delta** (str, optional) – Defines the timespan of the plots from today backwards. The passed argument is processed using pd.to_timedelta, defaults to 90 days.

    * **ylims_global** (bool, optional) – True to scale the y axis per parameter equally over all plants. False to scale each plot individually. Defaults to True.

    * **smoothingWnd** (float, optional) – optional, the window with for smoothing. Default for parameters E, S, T is 48h. L is not soothed by default. For individual adjustments, set smoothingWnd_E, smoothingWnd_S, smoothingWnd_L and/or smoothingWnd_T

    * **alphaOriginal** (float, optional) – optional, 0.3 by default to suplress the visibility of unsmoothed data.

    * **alphaSmoothed** (float, optional) – optional, 1.0 by default to highlight the plot of smoothed data.


The following parameters are typically pre set by the superseeding functions above.


* **Parameters**

    * **aggFunc** (str, optional) – 

    * **aggSpan** (str, optional) – 

    * **label_short** (bool, optional) – True to shorten the labels. False to use the long labels. Defaults to False.

    * **hide_ticks** (bool, optional) – True to all x and y labels and ticks from the plot. False to show. Defaults to False. Can be refined using hide_xTicks or hide_yTicks.

    * **time_labels** (str, optional) – “month” to show month on the major ticks and days as minor ticks.



#### plot_save(name, \*\*kwargs)
Stores the current figure.


* **Parameters**

    * **store** (bool) – True to store the plot. Defaults to False.

    * **outputdir** (str, optional) – The output directory for the plots, which can be generated. Defautls to “plots/”

    * **dpi** (int, optional) – The dpi of the plot, defaults to 300

    * **override_name** (str, optional) – Overwrites the default naming with this name.



#### rename_plants(rules=None)
Renames the plants based on the passed dict.


* **Parameters**

    **rules** (dict, optional) – a dict with the original and new names. If nothing is passed, the existing names are cropped after the first round bracket.
