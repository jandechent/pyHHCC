import HHCC
import logging
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
pd.set_option('display.width', 600)
pd.set_option('display.max_columns', 10)

hc = HHCC.HHCC("raw/")
hc.rename_plants()
hc.rename_plants({"Avocadobäumchen":"Avocado", "Yuccapalme":"Yucca"})

hc.plot_onePlant()
#hc.plot_allPlants()

#hc.rolling_mean(["24h", "48h", "72h"],"none","1h")
#hc.plot_onePlant(aggSpan="1h",store='ftp')
##hc.plot_onePlant(aggSpan="24h",aggFunc="mean")
#hc.plot_onePlant(aggSpan="72h",aggFunc="mean")

if False:
    hc.plot_onePlant_batch(store=True, time_delta="150days", light_as_integral=False)
    hc.plot_allPlants(store=True, light_as_integral=False)

if False:
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeTrue_lightintTrue", store=True, landscape=True,light_as_integral=True)
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeFalse_lightintTrue", store=True, landscape=False,light_as_integral=True)
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeTrue_lightintFalse", store=True, landscape=True,light_as_integral=False)
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeFalse_lightintFalse", store=True, landscape=False,light_as_integral=False)
    hc.plot_onePlant(override_name="plot_onePlant_lanscapeTrue_lightintFalse", store=True,  landscape=True,light_as_integral=False)
    hc.plot_onePlant(override_name="plot_onePlant_lanscapeFalse_lightintFalse", store=True, landscape=False,light_as_integral=False)
