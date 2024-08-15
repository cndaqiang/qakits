from matplotlib import pyplot as plt
#用于设置刻度间隔
from matplotlib.pyplot import MultipleLocator
import numpy as np
plt.switch_backend('agg')
class plotOB:
    def __init__(self):
        pass
    def plotXY(self,x,y):
        fig, ax = plt.subplots(1,1,sharex=True,sharey=False,figsize=(10,8))
        axs=[ax]
        axs[0].plot(x,y)
        return

