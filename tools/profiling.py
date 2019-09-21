import cProfile

import HHCC
import matplotlib.pyplot as plt

profRunInit=cProfile.run(
        "hc=HHCC.HHCC('raw/')",
        "HHCC.init.cprof")
profRunPlot=cProfile.run(
        "hc.plot_onePlant()",
        'HHCC.plotPlant.cprof')
profRunPlot=cProfile.run(
        "hc.plot_onePlant_oneParam(plt.gca(),hc.list_of_plants[0],'T')",
        'HHCC.plot_onePlant_oneParam.cprof')
#--> snakeviz