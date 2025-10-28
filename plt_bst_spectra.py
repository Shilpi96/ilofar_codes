##### the data is at https://data.lofar.ie
##### this code will plot bst spectra 
import datetime as datetime
import numpy as np
import struct
import os
import pdb
import time
import argparse
import matplotlib.pyplot as plt

def sb_to_freq(sb):
    nyq_zone = 1
    clock = 200
    freq = (nyq_zone-1+sb/512)*(clock/2)
    return freq

def sb_to_freqs(sb0, sb1, mode, clock_freq=200.0):
    modes = {3:0, 5:100, 7:200} # start frequency for each mode
    total_sbs = 512.0  # total number of subbands
    freqs = modes[mode] + np.arange(sb0, sb1+1)*clock_freq/(total_sbs*2.0)
    #freqs = freqs[::-11]
    return freqs


def build_spectrogram(path, filename, mode=3):
	#-------------------------------------------------#
	#
	# Supply path and name of bst file. Outputs data, 
	# time and freq array to be used in plot_spectro.
	#
	print('Building spectrogram from %s' %(path+filename))
	#--------------------------------#
	#
	#   Define mode frequencies
	## Sub-band numbers are set in the script that runs mode 3,5,7, or 357. Make sure they are the same
	## as the original observational setup!
	LBAlo_freqs = sb_to_freqs(51, 450, 3)  #sb_to_freqs(7, 494, 3)  
	HBAlo_freqs = sb_to_freqs(54, 452, 5)  #sb_to_freqs(54, 454, 5)
	HBAhi_freqs = sb_to_freqs(54, 228, 7)  #sb_to_freqs(54, 230, 7)


	fselect={
	    3:LBAlo_freqs,
	    5:HBAlo_freqs, 	   
	    7:HBAhi_freqs,
	    357:np.concatenate((LBAlo_freqs[::2], HBAlo_freqs[::2], HBAhi_freqs[::2])) # for mode 357
	     }
	freqs = fselect.get(mode, "Invalid mode")
	freqs = freqs[::-1]


	#----------------------------------#
	#
	#  Get file and build start_time
	#
	full_path = path + filename
	# extracting start time of observation from filename
	time_strp = time.strptime(filename[0:15], "%Y%m%d_%H%M%S")
	start_time = datetime.datetime(time_strp.tm_year, 
								   time_strp.tm_mon, 
								   time_strp.tm_mday, 
								   time_strp.tm_hour, 
								   time_strp.tm_min, 
								   time_strp.tm_sec)

	bit_mode = 8
	numbytes = os.path.getsize(full_path)		# Get the size of the file			
	numvals = numbytes//8 						# Get the number of values (each value is an 8-byte double)
	num_beamlets = 244*16//bit_mode          	# Determine the numger of beamlets (number of subbands)
	num_spectra = numvals//num_beamlets 		# Determine the number of time samples 
	datalen = num_spectra*num_beamlets  		# Use int division to clip-off surplus
	datastruct = str(int(numvals))+'d'         	# Used by struct.unpack to work out how to load
	time_resolution = 1.0                       # Seconds

	# Open the data file
	fp = open(full_path, 'rb')			# Read the raw data from the file into a buffer
	data = struct.unpack(datastruct, fp.read(numbytes))
	data = np.array(data)
	spill = len(data) - datalen
	if spill>0: data = data[0:-spill] # Sometimes data is not an integer multiple of spectra. This chops the incomplete spectrum off the end so that there's no problems for the reshape.
	numvals = numvals - spill
	data = np.reshape(data[:int(numvals)], (num_spectra, num_beamlets) )	# re-organise the raw data into an array that is easy to plot
	data = np.transpose(data)

	# Frequencies are generated from the subband or beamlets numbers used in the observation.
	# This could equal any number, 400 for example. The frequency array ends up being 400.
	# The data array is only generated (rehaped) correctly if we assume 488 subbands were used.
	# Seems as though the last 88 in this example are zero. Therefore the only observed data
	# are the first 0 to len(freq) are the only good data. Chop off the remainder.
	data = data[0:len(freqs),::]

	time_array = time.mktime( time.strptime(str(start_time), "%Y-%m-%d %H:%M:%S")) + np.arange(0, num_spectra)*time_resolution # 1 second per spectrum.

	data_dict = [{'data':data, 'time': time_array, 'freq':freqs, 'mode':str(mode)}]
	savefile = filename.split('.')[0]+'.npy'

	np.save(path+savefile, data_dict)
	print('Saved spectrogram in %s' %(path+savefile))
	fp.close()      # We don't need the file anymore, so close it

'''
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--file', default=None, type = str)
    parser.add_argument('--mode', default=357, type = int)
    args = parser.parse_args()
    
    path = os.path.dirname(args.file) + '/'
    filename = os.path.basename(args.file) # need to make this an option.
    result = build_spectrogram(path, filename, mode=args.mode)
    
'''
path='/home/shilpi/flare_ionospheric_project/'
filename='20240514_100136_bst_00X.dat'
result = build_spectrogram(path, filename, mode=357)
#plt.show()
