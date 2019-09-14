<!-- HHCC.py documentation master file, created by
sphinx-quickstart on Wed Aug 28 13:41:42 2019.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive. -->
# Documentation


#### class HHCC.HHCC(filename, outputdir='plots/', ignorePickled=False)

#### __init__(filename, outputdir='plots/', ignorePickled=False)

* **Parameters**

    * **filename** – Either directly a filename (without file extention) or a directory, 
      where the csv files are located. In case of a folder, 
      the csv file with the most recent “date modified” is used. 
      On second loading, a pickeld version of the data is loaded.

    * **outputdir** – The output directory for the plots, which can be generated.



* **Variables**

    * **listOfPlants** – a list with the names of all plants

    * **df** – the actual pandas dataframe, containing the parsed (hourly) data form the csv file.

    * **df_daily** – a pandas dataframe, containing aggregated data per day. See `HHCC.__calcDaily()` for details.

    * **minMax** – For plotting we need to know the global min and max values per plotted value and per aggregation. 
      [“daily”,hc.L,”sum”,”amax”] gives you the maximum values that will ever be plotted for plots that 
      show daily data for the sum of light.

    * **E** – the column name for the parameter on conductivity

    * **L** – the column name for the parameter on light

    * **S** – the column name for the parameter on humidity

    * **T** – the column name for the parameter on temperature



* **Returns**

    the object that includes the parsed data.



#### consistencyCheck()
Checks `HHCC.df` for consistency: The sensor can only store data for ?30? days. Therefore, warn the user to sync soon enough (15 days).


* **Returns**

    Nothing, but there might output from the logger.



#### plotAllPlants(timeDelta='25days', store=False, lightAsIntegral=True, ylims='global')
calls `HHCC.plotPlant()` for all available plants.


* **Parameters**

    **ylims** – Can be “gloabl” to unify the yscaling for all plots. If it is somethingn else,
    each plot is scaled individually long the y axis.



* **Returns**

    Nothing, but outputs the plots and potentially writes files.



#### plotPlant(plant, timeDelta='90days', store=False, lightAsIntegral=True, ylims='individual')
Generates one plot of the four parameters light, temperature, nutrition and light over time.


* **Parameters**

    * **plant** – Name of the plant (for names, check `HHCC.listOfPlants`)

    * **timeDelta** – The time axis spans from today till today - timeDelta. The timeDelta must be readable by `pandas.to_timedelta()`

    * **store** – If set to true, the plot is stored as png to the folder give in `HHCC.outputdir`

    * **ylims** – Can be “gloabl” to unify the yscaling for all plots. If it is somethingn else,
      each plot is scaled individually long the y axis.



* **Returns**

    Nothing



#### __weakref__()
list of weak references to the object (if defined)

## Private


#### class HHCC.HHCC(filename, outputdir='plots/', ignorePickled=False)

#### _HHCC__aggregateData()
The raw data are provided on an hourly basis, this function aggregates the data from `HHCC.df` into the variable
`HHCC.df_daily`
\* E: Conducticity, aka “nutrition” is aggretated, using np.mean
\* L: Light is aggregated using the np.sum function. 
\* S: Humidity is aggregated using np.mean
\* T: Temperature is aggregated using np.mean


* **Returns**

    Nothing, directly writed into `HHCC.dfa`



#### _HHCC__aggretagateAppendHelper(df, aggFunc, aggFunc_label, aggSpan)

* **Parameters**

    * **df** – dataframe

    * **aggFunc** – the actual aggretation function

    * **aggSpan** – the label used, should be the same as aggfunc or more beautiful.

    * **span** – the interval of avergaging: daily, monthly, yearly



* **Returns**

    Nothing, directly writed into `HHCC.dfa`



#### _HHCC__deleteSensorFails(originalUnits)
Deletes data points, where there was a sensor failure.


* **Parameters**

    **originalUnits** – If true, assumes the original units. Otherwise, it is mol for light and ms/cm for conductivity



* **Returns**

    Nothing. Data are directly changed in `HHCC.df`



#### _HHCC__load(filepath)
Loads the data of the passed in filename


* **Parameters**

    **filepath** – full path + filename, including file extension



* **Returns**

    Nothing. Data are directly stored in `HHCC.df`



#### _HHCC__makeMinMax()
sdf


* **Returns**

    Nothing.



#### _HHCC__plotPlantHelper(ax, param, df, aggFunc, aggSpan, startTime, endTime, ylims='global')

* **Parameters**

    **ylims** – Can be “gloabl” to unify the yscaling for all plots. If it is somethingn else,
    each plot is scaled individually long the y axis.



#### consistencyCheck()
Checks `HHCC.df` for consistency: The sensor can only store data for ?30? days. Therefore, warn the user to sync soon enough (15 days).


* **Returns**

    Nothing, but there might output from the logger.



#### plotAllPlants(timeDelta='25days', store=False, lightAsIntegral=True, ylims='global')
calls `HHCC.plotPlant()` for all available plants.


* **Parameters**

    **ylims** – Can be “gloabl” to unify the yscaling for all plots. If it is somethingn else,
    each plot is scaled individually long the y axis.



* **Returns**

    Nothing, but outputs the plots and potentially writes files.



#### plotPlant(plant, timeDelta='90days', store=False, lightAsIntegral=True, ylims='individual')
Generates one plot of the four parameters light, temperature, nutrition and light over time.


* **Parameters**

    * **plant** – Name of the plant (for names, check `HHCC.listOfPlants`)

    * **timeDelta** – The time axis spans from today till today - timeDelta. The timeDelta must be readable by `pandas.to_timedelta()`

    * **store** – If set to true, the plot is stored as png to the folder give in `HHCC.outputdir`

    * **ylims** – Can be “gloabl” to unify the yscaling for all plots. If it is somethingn else,
      each plot is scaled individually long the y axis.



* **Returns**

    Nothing
