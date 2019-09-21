# pyHHCC
Can generate various overview plots for the plant and parameters provided from
the export of the FlowerCare app by Xiaomi/HHCC. The [full documentation is provided here](https://github.com/jandechent/HHCC.py/blob/master/docs/markdown/index.md),
here is a quick example:
```python
from pyHHCC import pyHHCC
hc = pyHHCC("2019-08-25-04-HHCC")
hc.plot_onePlant()
```
![plot_onePlant](https://raw.githubusercontent.com/jandechent/HHCC.py/master/examples/plot_onePlant.jpg)
```python
hc.plot_allPlants(light_as_integral=True)
```
![plot_allPlants](https://raw.githubusercontent.com/jandechent/HHCC.py/master/examples/plot_allPlants.jpg)
