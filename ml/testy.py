import sys
sys.path.append("..")

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

dataset = pd.read_csv('../output/car_258833.csv')

x = dataset.iloc[:,:].values