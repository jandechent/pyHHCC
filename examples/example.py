from pyHHCC import pyHHCC

if __name__ == '__main__' :
    # some improvements to logging and outout of pandas dataframes:
    import logging
    import pandas as pd
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(name)s-%(lineno)4d-%(levelname)7s: %(message)s')
    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.WARNING)
    pd.set_option('display.width', 600)
    pd.set_option('display.max_columns', 10)

hc = pyHHCC("examples/example")
hc.plot_onePlant()
hc.plot_onePlant(aggSpan="48h", aggFunc="mean")

if False:
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeTrue_lightintTrue", store=True, landscape=True,light_as_integral=True)
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeFalse_lightintTrue", store=True, landscape=False,light_as_integral=True)
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeTrue_lightintFalse", store=True, landscape=True,light_as_integral=False)
    hc.plot_allPlants(override_name="plot_allPlants_lanscapeFalse_lightintFalse", store=True, landscape=False,light_as_integral=False)
    hc.plot_onePlant(override_name="plot_onePlant_lanscapeTrue_lightintFalse", store=True,  landscape=True,light_as_integral=False)
    hc.plot_onePlant(override_name="plot_onePlant_lanscapeFalse_lightintFalse", store=True, landscape=False,light_as_integral=False)
