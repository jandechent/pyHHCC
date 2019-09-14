import HHCC
import cProfile
import pstats

#hc=HHCC.HHCC("raw/")

profRunInit=cProfile.run("hc=HHCC.HHCC('raw/')","HHCC.init.cProfile")
p = pstats.Stats('HHCC.init.cProfile')
p.sort_stats('cumulative').print_stats(30)
p.sort_stats('time').print_stats(10)

profRunPlot=cProfile.run("hc.plot_onePlant()",'HHCC.plotPlant.cProfile')
p = pstats.Stats('HHCC.plotPlant.cProfile')
p.sort_stats('cumulative').print_stats(30)
p.sort_stats('time').print_stats(10)
