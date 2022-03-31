# -*- coding: cp1252 -*-
import matplotlib as mpl
mpl.use('Agg')
import numpy
from pylab import figure, ylim, show, savefig, plot_date, date2num,twinx,contour,legend,colorbar
#from Scientific.IO.NetCDF import NetCDFFile as NCDataset
from netCDF4 import Dataset as NCDataset
from matplotlib.dates import YearLocator, MonthLocator,DayLocator,HourLocator,MinuteLocator,DateFormatter
from matplotlib.ticker import AutoLocator, MultipleLocator, FixedLocator
#from matplotlib.colors import LogNorm
from numpy import *
#import array
import datetime as dt
import time as tm
from sys import exit, argv
import os
import math
import argparse

def get_unix_time(year,month,day,hour,minute,second):
    unixtime = dt.datetime(year,month,day,hour,minute,second)
    return unixtime.replace(tzinfo=dt.timezone.utc).timestamp()

def get_nc_files(folders,s_unix, e_unix):

    s_time=tm.localtime(s_unix)
    e_time=tm.localtime(e_unix)
    
    s_date=dt.date(s_time[0],s_time[1], s_time[2])
    e_date=dt.date(e_time[0],e_time[1], e_time[2])

    ncfiles  = []
    thistime = s_unix 
    for n in range( (e_date-s_date).days+1 ):
        t   = s_date+dt.timedelta(n)
        s_year  = str(t.year).zfill(4)
        s_month = str(t.month).zfill(2)
        s_day   = str(t.day).zfill(2)
        ncfile  = folders['datafolder']+s_year+'/'+s_year+s_month+s_day+'_disdrometer.nc'
        if os.path.exists(ncfile):
            ncfiles.append(ncfile)
    #print  ncfiles
    return ncfiles

def append_data(thisvar,newvar):
    n_dim=len(thisvar.shape)
    if n_dim == 1:
        return numpy.append(thisvar,newvar)
    if n_dim == 2:
        thisvar=numpy.concatenate((thisvar,newvar), axis=0)
    return thisvar
    
def get_nc_data(ncfiles, varname):
    requested_var = None
    for thisfile in ncfiles:
        ncfile = NCDataset(thisfile,'r')
        var    = ncfile.variables[varname]
        if requested_var != None:
            requested_var=append_data(requested_var,var[:])
        else:
            requested_var=var[:]
    return requested_var


def get_xtick_interval(xmin,xmax):
    nticks  = 8
    deltat  = (xmax-xmin)*24.
    #delta_h = int(math.ceil(deltat/nticks)) 
    delta_h = deltat/nticks
    if delta_h > 0.5:
        return ('hour',int(math.ceil(delta_h)),)
    if delta_h <= 0.5:
        return ('minute',int(math.ceil(deltat*60)/nticks),)
    #print 'delta_h in get_xtick_interval: ', delta_h
    #return delta_h


def plot2d (x,y,xmin,xmax,xtitle,ytitle,varname):
#x: unixtime
    #d = [dt.datetime.fromtimestamp(tm.mktime(tm.localtime(i))) for i in x]
    #d = mpl.dates.date2num(d)

    fig   = figure(figsize=(10,3.5),dpi=80,facecolor='w',edgecolor='k')    

    ax = fig.add_subplot(111)

    delta_h=get_xtick_interval(x[0],x[-1])
    
    if delta_h[0] == 'minute':
        major    = MinuteLocator(range(0,60,delta_h[1]))
        minor    = MinuteLocator()
 
    if delta_h[0] == 'hour':
        major   = HourLocator(range(0,24,delta_h[1]))
        minor   = MinuteLocator(interval=30)

    daysFmt = DateFormatter('%d.%m.%y\n%H:%M UT')   
    
    ax.xaxis.set_minor_locator(minor)       
    ax.xaxis.set_major_locator(major)
    ax.xaxis.set_major_formatter(daysFmt)
    

    
    ylocator=AutoLocator()

    ax.set_ylabel(ytitle)
    font={'family': 'sans-serif',
          'weight': 'bold',
          'size': 10}
    mpl.rc('font',**font)

    ax.yaxis.grid(True)
    ax.xaxis.grid(True)

    ax.plot_date(x,y,'-')#,tz='local')

    ax.yaxis.set_major_locator(ylocator)
    y_major  = ax.yaxis.get_majorticklocs()
    dy_minor = (y_major[-1]-y_major[0])/(len(y_major)-1)/5.
    ax.yaxis.set_minor_locator(MultipleLocator(dy_minor)) 
   
    #fig.show()
    fig.savefig(folders['imagefolder']+varname+'.png')


def plotcontour (x,y,z,xmin,xmax,xtitle,ytitle,varname):


    z=transpose(z)

    if varname == 'number_concentration':
        z=z[0:len(y)-1,:]        
        y=y[0:len(y)-1]

    y_max=0
    for i in range(len(y)):
        if y[i] > y_max:
            y_max=y[i]
    z_max=0
    i_max=0
    for i in range(len(z[:,0])):
        for j in range(len(z[i,:])):
            if z[i,j] > z_max:
                z_max=z[i,j]
            if z[i,j] <= 0:
                z[i,j]=float('NaN')
            if z[i,j] > 0:
                if i > i_max:
                    i_max=i
    if i_max == 0:
        i_max=len(y)-1
    if z_max == 0:
        z_max=0.1

    y_max = y[i_max]
    z     = z[0:i_max,:]
    y     = y[0:i_max]
    #d = [dt.datetime.fromtimestamp(tm.mktime(tm.localtime(i))) for i in x]
    #d = mpl.dates.date2num(d)

    fig   = figure(figsize=(10,3.5),dpi=80,facecolor='w',edgecolor='k')    
    
    if varname == 'number_concentration':
        title='number concentration'
        cb_label='log(1/(m^3 mm))'
    if varname == 'fall_velocity':
        title='velocity distribution'
        cb_label='m/s'
        
    ax = fig.add_subplot(111,title=title)

    delta_h=get_xtick_interval(x[0],x[-1])
    
    if delta_h[0] == 'minute':
        major    = MinuteLocator(range(0,60,delta_h[1]))
        minor    = MinuteLocator()
        daysFmt  = DateFormatter('%d.%m.%y\n%H:%M UT')
 
    if delta_h[0] == 'hour':
        major   = HourLocator(range(0,24,delta_h[1]))
        minor    = MinuteLocator(interval=30)
        daysFmt = DateFormatter('%d.%m.%y\n%H:%M UT')
    
    ax.xaxis.set_minor_locator(minor)       
    ax.xaxis.set_major_locator(major)
    ax.xaxis.set_major_formatter(daysFmt)

    ylocator=AutoLocator()

    ax.set_ylabel(ytitle)
    font={'family': 'sans-serif',
          'weight': 'bold',
          'size': 10}
    mpl.rc('font',**font)

    ax.yaxis.grid(True)
    ax.xaxis.grid(True)

    levels=[]
    n_levels=8
    z_min=0
    for i in range(n_levels):
        levels.append(z_min+i*z_max/n_levels)
    ax.set_ylim([0,y_max])
    #ax.yaxis.set_major_locator(ylocator)
    #y_major  = ax.yaxis.get_majorticklocs()
    #dy_minor = (y_major[-1]-y_major[0])/(len(y_major)-1)/5.
    #ax.yaxis.set_minor_locator(MultipleLocator(dy_minor))

    #levels=[0,0.5,1,1.5,2,2.5,3]
    if varname == 'number_concentration':
        CS=ax.contourf(x,y,z,levels)
    if varname == 'fall_velocity':
        CS=ax.contourf(x,y,z,levels)

    CS.cmap.set_under('white')
    CS.cmap.set_over('red')
    cb=fig.colorbar(CS)
    cb.ax.set_ylabel(cb_label)
    #fig.show()
    fig.savefig(folders['imagefolder']+varname+'.png')

    

def get_and_plot_data(ncfiles,Unix_time,plot_time,var,start,end):
    diameters=[0.062,0.187,0.312,0.437,0.562,0.687,0.812,0.937,1.062,1.187,1.375,
               1.625,1.875,2.125,2.375,2.750,3.250,3.750,4.250,4.750,5.500,6.500,
               7.500,8.500,9.500,11.000,13.000,15.000,17.000,19.000,21.500,24.500]
    velocities=[0.05,0.15,0.23,0.35,0.45,0.55,0.65,0.75,0.85,0.95,1.1,1.3,1.5,1.7,
                1.9,2.2,2.6,3.0,3.4,3.8,4.4,5.2,6.0,6.8,7.6,8.8,10.4,12.0,13.6,15.2,
                17.6,20.8]

    data = get_nc_data(ncfiles,var)

    if var == 'rainfall_rate':
        data=data*1000*3600 # Convert from m/s to mm/s to mm/hr 

    #if var == 'number_concentration':
    #    ytitle='Drop Diameter [mm]'
    if var == 'fall_velocity':
        ytitle='Hydrometeor Diameter [mm]'
    if var == 'rainfall_rate':
        ytitle='Precipitation Rate [mm/h]'
    if var == 'radar_reflectivity':
        ytitle='Equivalent Radar Reflectivity [dBz]'
    if var == 'n_particles':
        ytitle='Number of Detected Particles'
    if var == 'number_concentration':
        ytitle='Hydrometeor Diameter [mm]'
    if   var == 'rainfall_rate' or var == 'radar_reflectivity' or var == 'n_particles':
        plot2d(plot_time,data[start:end],0,0,'Time',ytitle,var)
    if   var == 'number_concentration' or var == 'fall_velocity':
        plotcontour(plot_time,diameters, data[start:end,:],0,0,'Time',ytitle,var)
    return data



def get_xrange(args):
    #no starting time    
    if not args.timestamp_s:
        #print "No start timestamp given."
        #no ending time
        if not args.timestamp_e:
            #print "No end timestamp given."
            #no duration
            if not args.duration:
                #print "No duration given. Using standard value: 12"
                args.duration    = default_duration
            #set ending time to current time
            args.timestamp_e = tm.time()
        #ending time is available   
        else:
            args.timestamp_e=get_unix_time(int(args.timestamp_e[0:4]),int(args.timestamp_e[4:6]),
                                           int(args.timestamp_e[6:8]),int(args.timestamp_e[8:10])
                                           ,int(args.timestamp_e[10:12]),0)
        #no duration available
        if not args.duration:
            #print "No duration given. Using standard value: 12"
            args.duration  = default_duration
        #set starting time to current time - duration        
        args.timestamp_s = args.timestamp_e-args.duration*3600.
    else:
        args.timestamp_s=get_unix_time(int(args.timestamp_s[0:4]),int(args.timestamp_s[4:6]),
                                       int(args.timestamp_s[6:8]),int(args.timestamp_s[8:10])
                                       ,int(args.timestamp_s[10:12]),0)
        #print args.timestamp_s
        #no ending time available
        if not args.timestamp_e:
            #no duration available
            if not args.duration:
                args.duration  = default_duration
            #print args.duration
            args.timestamp_e = args.timestamp_s+args.duration*3600.
        else:
            args.timestamp_e=get_unix_time(int(args.timestamp_e[0:4]),int(args.timestamp_e[4:6]),
                                           int(args.timestamp_e[6:8]),int(args.timestamp_e[8:10])
                                           ,int(args.timestamp_e[10:12]),0)        
        args.duration=args.timestamp_e-args.timestamp_s                                           
    return args            

def define_parser(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('-e', action='store', dest='timestamp_e', 
                        help='end time yyyymmddhhmm')
    
    parser.add_argument('-s', action='store', dest='timestamp_s', 
                        help='starting time yyyymmddhhmm')
    
    parser.add_argument('-d', action='store', dest='duration', type=float,
                        help='time interval to display in hours')
    return parser



'''*********************'''
'''START OF MAIN PROGRAM'''
'''*********************'''
#-s 201202170200 -d 10

#provide input variables
#datafolder='C:\\Users\\Vaio\\Desktop\\PlotParsivel\\'
#datafolder='G:\\Programme\\Python\\PlotParsivel\\'
#datafolder='/home/cloudnet/data/meteo/'

datafolder='/home/disdrometer/data/'
imagefolder='/home/disdrometer/tmp/'
folders={'datafolder':datafolder, 'imagefolder':imagefolder}

default_duration=12

# process command line arguments
parser = define_parser(argv)
# extract argument structure from parser
args   = parser.parse_args()

# determine start time (xmin) and end time (xmax) of plot 
times  = get_xrange(args)        

ncfiles   = get_nc_files(folders,times.timestamp_s, times.timestamp_e)
print(ncfiles)
Unix_time = get_nc_data(ncfiles, 'time')*1.


#reduce data
start = where(Unix_time >= times.timestamp_s)
if len(start[0]) == 0:
        print('Start time not found in data...exiting')
        exit()
start = start[0][0]

end   = where(Unix_time >= times.timestamp_e)
if len(end[0]) == 0:
        end = len(Unix_time)-1
else:
        end = end[0][0]

plot_time = [dt.datetime.fromtimestamp(tm.mktime(tm.localtime(i))) for i in Unix_time[start:end]]
plot_time = mpl.dates.date2num(plot_time)

RR        = get_and_plot_data(ncfiles,Unix_time,plot_time,'rainfall_rate',start,end)
Ze        = get_and_plot_data(ncfiles,Unix_time,plot_time,'radar_reflectivity',start,end)
N         = get_and_plot_data(ncfiles,Unix_time,plot_time,'n_particles',start,end)
N_Field   = get_and_plot_data(ncfiles,Unix_time,plot_time,'number_concentration',start,end)
V_Field   = get_and_plot_data(ncfiles,Unix_time,plot_time,'fall_velocity',start,end)

R=RR*0
time_interval=get_nc_data(ncfiles, 'interval')*1.
for i in range(1,len(RR)):
    R[i]=R[i-1]+RR[i]*time_interval[i]/3600.
ytitle='Accumulated precip. [mm]'
var='acc_precip'
plot2d(plot_time,R[start:end],0,0,'Time',ytitle,var)
