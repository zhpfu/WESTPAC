import sys
#sys.path.append('/usr/lib/python2.7/site-packages/mpl_toolkits/')
#sys.path.append('/usr/lib/python2.7/site-packages/')
import fnmatch
import os
import glob
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap, cm
#import mpl_toolkits
#mpl_toolkits.__path__.append('/usr/lib/python2.7/site-packages/mpl_toolkits/')
from mpl_toolkits.basemap import Basemap,cm
import matplotlib.cm as cm
import numpy as np
from matplotlib.patches import Polygon
from netCDF4 import Dataset, num2date, netcdftime
import datetime
import matplotlib.path as mpath
import matplotlib
from scipy.interpolate import spline


#For days in each MJO phase, count the number of days on which the rainfall exceeded the 95th percentile of climatology for that day
#Convert this to the percentage of days on which the rainfall exceeded the 95th percentile of climatology for that day

#We can then later plot the bias in probability i.e. the probability in this MJO phase - 5% (the climatological probability of exceeding the 95th percentile is 5%)
#To see whether the probability is increased or decreased during each phase of the MJO, of having extreme rainfall 

#This version uses the 95th percentile that is calculated across the whole year (rather than the 95th percentile for a given day across all years)
#And all values below 1mm of rainfall were removed before calculating the 95th percentile

IMERG_DIR = "/gws/nopw/j04/klingaman/emerton/GPM-IMERG/"





BSISO_FILE = "/gws/nopw/j04/klingaman/datasets/BSISO_INDICES/bsiso_indices.jan-dec_dmeans_ts.1981-2019.nc"

print BSISO_FILE

ffBSISO = Dataset(BSISO_FILE,'r')
BSISOdatesnc = ffBSISO.variables['time'][:]

BSISO_amp_data = ffBSISO.variables['bsiso1_amp'][:]
BSISO_phase_data = ffBSISO.variables['bsiso1_phase'][:]


#I want the phase and amplitude of PAIR 1 (?!) of the BSISO, as there are two BSISO indices? see Lee et al., 2013
#The file has some variables I'm unsure of, i.e. 'Component 1 / Component 2 of the BSISO 1 index" - I think these come together to give the overall amplitude that I use, like the MJO
#and also amp_0 of BSISO 1 index. What is the difference between amp and amp_0? The variable descriptions are the same. I have used 'amp' for now. 

t_unit = ffBSISO.variables['time'].units
t_cal = ffBSISO.variables['time'].calendar
tvalue = num2date(BSISOdatesnc, units=t_unit, calendar=t_cal)

BSISOdates = [i.strftime("%Y-%m-%d") for i in tvalue]

ffBSISO.close()



years = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019] #,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018
years = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019] #,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018
ENyears=[2002, 2009, 2015]
LNyears=[2007, 2010, 2011, 2017]
	
def compute_probabilities(year_array, BSISO1, BSISO2): #1,2,3,4,5,6,7,8
	#print MJOdates
	
	#array to hold the total number of days in this MJO phase, at each gridpoint, that had rainfall exceeding the 95th percentile of climatology
	no_days_exceeding_pctl = np.zeros((1440,400))
	
	#we also want to know the total number of days in this MJO phase, so we can calculate what % of them had extreme rainfall
	total_no_days = 0 #number of days included in thesum, in order to compute the mean
	
	MONTHLY_CLIM_ARRAY = np.zeros((6,1440,400))

	IMERG_CLIM_DIR = "/gws/nopw/j04/klingaman/emerton/GPM-IMERG/"

	for m,i in zip([4,5,6,7,8,9],[0,1,2,3,4,5]):
		
		if year_array == ENyears:
			#IMERG_CLIM_FILE = IMERG_CLIM_DIR+"GPM_IMERG.DAILY.TRMM_GRID.2001-2019.m0"+str(m)+".95th_percentile.nc"
			IMERG_CLIM_FILE = IMERG_CLIM_DIR+"GPM_IMERG_DAILY.TRMM_grid.ElNinoYears.*.m0"+str(m)+".95th_percentile.nc"
			IMERG_CLIM_FILE = glob.glob(IMERG_CLIM_FILE)[0]
			print IMERG_CLIM_FILE
				
		elif year_array == LNyears:
			IMERG_CLIM_FILE = IMERG_CLIM_DIR+"GPM_IMERG_DAILY.TRMM_grid.LaNinaYears.*.m0"+str(m)+".95th_percentile.nc"
			print IMERG_CLIM_FILE
			IMERG_CLIM_FILE = glob.glob(IMERG_CLIM_FILE)[0]
				

		print IMERG_CLIM_FILE

		ffCLIM = Dataset(IMERG_CLIM_FILE,'r')

		CLIM = ffCLIM.variables['precipitationCal'][:]
	
		MONTHLY_CLIM_ARRAY[i,:,:] = CLIM

		ffCLIM.close() 

	for year in year_array: #
	

	
		year=year+1 #the year arrays list the year the El Nino / La Nina event started ,but we're interested in the summer after the event started, 
		#as it's decaying/after it's decayed 
	
		imerg_file = IMERG_DIR+"GPM_IMERG_3B-DAY.MS.MRG.3IMERG."+str(year)+".DAILY.V06_regridded_to_TRMM_grid.nc"
		print imerg_file
		
		ff_imerg = Dataset(imerg_file,'r')
		
		daily_rain = ff_imerg.variables['precipitationCal'][:]
			
		start_time = datetime.datetime(year,1,1)
		imerg_tvalue = np.array([start_time + datetime.timedelta(days=i) for i in xrange(len(daily_rain[:,0,0]))])
			
		imerg_dates = [j.strftime("%Y-%m-%d") for j in imerg_tvalue]
		
		ff_imerg.close()
		
		print np.shape(daily_rain)
		print np.shape(MONTHLY_CLIM_ARRAY)
			

		summer_start_date = imerg_dates.index(str(year)+'-04-01')
		summer_end_date = imerg_dates.index(str(year)+'-09-30')
	
	
		#we want to run this only for dates in 'extended summer' - so we want to run April 1st to September 30th
		#For winter, we needed two loops since this crosses the end of the file, but don't need to do this for summer
		
		#Found the index for the first of August, loop over this date to the end of the array	
		for date in imerg_dates[summer_start_date:summer_end_date]:
		
		
			#print date
			
			dateinfo = datetime.datetime.strptime(date, "%Y-%m-%d")
			
			if dateinfo.strftime("%m") == '04':
				ci = 0
			elif dateinfo.strftime("%m") == '05':
				ci = 1
			elif dateinfo.strftime("%m") == '06':
				ci = 2
			elif dateinfo.strftime("%m") == '07':
				ci = 3
			elif dateinfo.strftime("%m") == '08':
				ci = 4
			elif dateinfo.strftime("%m") == '09':
				ci = 5
			else:
				print "month is ", dateinfo.strftime("%m")
			
			if dateinfo.strftime("%m-%d") == '02-29': #leap year 29th Febs missing in MJO data
			
				continue
				
			else:
				i = BSISOdates.index(date)  #np.where(MJOdates = date)
		
				BSISO_phase = BSISO_phase_data[i]
				BSISO_amp = BSISO_amp_data[i]
			
				#print mjo_amp
				
				if (BSISO_phase == BSISO1 or BSISO_phase == BSISO2) and BSISO_amp >= 1.0:
				
					print BSISO_phase
					print BSISO_amp
				
					total_no_days += 1
				
					print date
			
					a = imerg_dates.index(date)
					
					for x in range(1440):
						for y in range(400):
							
							#if the daily rainfall on this day and at this location,is equal to or above the 95th percentile of climatology for this day, 
							#add one to the array that holds the total number of days exceedingthe 95th percentile at each gridpoint
							
							if daily_rain[a,x,y] >= MONTHLY_CLIM_ARRAY[ci,x,y]:
								no_days_exceeding_pctl[x,y] += 1
								
							#otherwise, do nothing, we're only interested in finding out how many days exceeded the 95th percentile during this MJO phase
							else:
								continue
							
								
			
						
	
					
				#if the MJO amplitude for this phase is <1 on this day, we're not interested so carry on
				else:
			
					continue
				
		
	print total_no_days
	print no_days_exceeding_pctl
	print np.nanmax(no_days_exceeding_pctl)
	
	
	#convert the number of days exceeding the 95th percnetile, to the % of days exceeding the 95th percentils
	
	perc_days_exc_pctl = np.zeros((1440,400))
	
	for x in range(1440):
		for y in range(400):
		
			perc_days_exc_pctl[x,y] = (no_days_exceeding_pctl[x,y] / total_no_days) * 100
			
			
	if year_array==ENyears:
		enso_label='elnino_years_1.0_ONI_threshold'
	elif year_array==LNyears:
		enso_label='lanina_years_1.0_ONI_threshold'
			
	np.savetxt("gpm-imerg.precip_composite.percentage_of_days_exceeding_95th_percentile.COMBINED_ENSO_BSISO.BSISO_phase_"+str(BSISO1)+str(BSISO2)+"."+enso_label+"."+str(total_no_days).zfill(4)+"-days.TRMM_grid.April-Sept.MONTHLY_ENSO_YEARS_ONLY_percentiles.txt",  perc_days_exc_pctl[:,:], '%.4f')
	
						
			
#compute_probabilities(ENyears,1,2)
#compute_probabilities(ENyears,3,4)
#compute_probabilities(ENyears,5,6)
#compute_probabilities(ENyears,7,8)

#compute_probabilities(LNyears,1,2)
#compute_probabilities(LNyears,3,4)
#compute_probabilities(LNyears,5,6)
compute_probabilities(LNyears,7,8)	
			
	
			
			
		



