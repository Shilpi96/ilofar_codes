### First run read_bst_data.py and get .npy files
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pdb
from matplotlib.colors import LogNorm
from matplotlib import dates
def freq_axis(freqs):
	freqs = freqs[::-1]
	gap1 = np.flipud(freqs[288]+(np.arange(59)*0.390625)) 
	gap2 = np.flipud(freqs[88]+(np.arange(57)*0.390625))
	ax_shape = 59+57-1
	new_freq = np.zeros(ax_shape+freqs.shape[0])
	#pdb.set_trace()
	new_freq[0:88] = freqs[0:88]
	new_freq[88:145]  = gap2[:57]
	new_freq[145:345] = freqs[88:288]
	new_freq[345:404] = gap1[:59]
	new_freq[404:] = freqs[289:]
	return new_freq

def data_expand(data):
	data = np.flipud(data)
	data[np.where(np.isinf(data)==True)] = 0.0
	data2 = np.empty((freq.shape[0], data.shape[1]))    
   
	data2[:] = np.nan
	data2[0:88] = data[0:88]
	data2[145:345] = data[88:288]
	data2[404:] = data[289:]
	return data2

def backsub(data, percentile=5.0):

    # Get time slices with less than or equal to the bottom nth percentile.
    # Get average spectra from these time slices.
    # Devide through by this average spec.
    # Expects (row, column)

    print('Performing background subtraction.')
    percentiles = np.percentile(data, percentile, axis=1)
    values_below_percentile = [row[row <= p] for row, p in zip(data, percentiles)]
    meanlist = [np.median(values_below_percentile[i]) for i in range(len(values_below_percentile))]
    meanarray = np.array(meanlist)
    meanarray = meanarray[:, np.newaxis]
    
    data = data/meanarray
    
    print('Background subtraction finished.')
    return data
path = '/Users/shilpibhunia/Documents/projects/March_2025_campaign/event_2025_03_26/ilofar_data/'
npy_data = np.load(path+'20250326_083037_bst_00X.npy',allow_pickle=True)
freqs = npy_data[0]['freq']
freq = freq_axis(freqs)

data = npy_data[0]['data']
data = data_expand(data)
data = backsub(data, percentile=5.0)

time = npy_data[0]['time']
times = np.array([datetime.fromtimestamp(t) for t in time])


fig = plt.figure(figsize=(12, 7))
ax1 = fig.add_subplot(111)
#vmm = np.percentile(data, [1,96])
peak1 = ax1.imshow(np.log10(data),cmap=plt.get_cmap('viridis'), aspect = 'auto', origin = 'lower',
       extent=(times[0], times[-1], freq[-1], freq[0]))
#cbar_ax = fig.add_axes([0.91, 0.1, 0.02, 0.4])
#cbar = fig.colorbar(peak1, cax=cbar_ax)
ax1.xaxis.set_major_locator(dates.MinuteLocator(interval=10))
ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
startt = datetime(2025,3,26, 9,7,14)
endt = datetime(2025,3,26, 9,50)
ax1.set_xlim(startt,times[-1])
#ax1.set_ylim(110,165)
plt.show()
#pdb.set_trace()
