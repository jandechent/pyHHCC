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
hc.plot_onePlant(override_name="plot_onePlant_hourly", outputdir="examples/", store=True)
hc.plot_onePlant(aggSpan="48h", aggFunc="mean", override_name="plot_onePlant_mean_over_48h", outputdir="examples/", store=True)
