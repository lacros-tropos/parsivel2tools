import serial
import io
import time
import datetime
from array import array
import os
#from Scientific.IO.NetCDF import NetCDFFile as NCDataset
from netCDF4 import Dataset as NCDataset
from numpy import *

def ToFloat(a):
    newarray=[]
    for i in a:
        if len(i) > 0:
            newarray.append(float(i))
    return newarray

def ToLong(a):
    newarray=[]
    for i in a:
        if len(i) > 0:
            newarray.append(int(i))
    return newarray

def write_nc(rootfolder, newdata):
    dir=rootfolder+time.strftime("%Y",time.gmtime(newdata['UnixTime']))
    if not os.path.exists(dir):
        os.mkdir(dir)
    #dir=dir+'/'+time.strftime("%m",time.gmtime(newdata['UnixTime']))
    #if not os.path.exists(dir):
    #    os.mkdir(dir)
    #Create NC File 
    ncfilename=dir+'/'+time.strftime("%Y%m%d",time.gmtime(newdata['UnixTime_bnds'][0][0]))+'_disdrometer'+'.nc'
    print('Writing to File: ', ncfilename, ' at ', time.strftime("%H:%M:%S",time.gmtime(newdata['UnixTime'])))

    if os.path.exists(ncfilename):
        ncfile = NCDataset(ncfilename,'a', format='NETCDF3_CLASSIC')

        #get length of unlimited dimension time
        idx_unlimited_dim=ncfile.dimensions['time'].size

        varNames= ncfile.variables.keys()
        for variable in varNames:
            var=ncfile.variables[variable]
            if variable == 'time': 
                var[idx_unlimited_dim]=(newdata['UnixTime'])
            if variable == 'time_bnds':
                var[idx_unlimited_dim,:]=(newdata['UnixTime_bnds'][0][:])
            if variable == 'interval':
                var[idx_unlimited_dim]=(newdata['Interval'])
            if variable == 'data_raw':
                var[idx_unlimited_dim,:,:]=(newdata['RawData'])
            if variable == 'number_concentration':
                var[idx_unlimited_dim,:]=(newdata['N_Field'])
            if variable == 'fall_velocity':
                var[idx_unlimited_dim,:]=(newdata['V_Field'])
            if variable == 'n_particles':
                var[idx_unlimited_dim]=(newdata['NParticles'])
            if variable == 'rainfall_rate':
                var[idx_unlimited_dim]=(newdata['RR_Intense'])
            if variable == 'radar_reflectivity':
                var[idx_unlimited_dim]=(newdata['dBZ'])
            if variable == 'E_kin':
                var[idx_unlimited_dim]=(newdata['E_kin'])
            if variable == 'visibility':
                var[idx_unlimited_dim]=(newdata['MOR'])
            if variable == 'synop_WaWa':
                var[idx_unlimited_dim]=(newdata['SYNOP_WaWa'])
            if variable == 'synop_WW':
                var[idx_unlimited_dim]=(newdata['SYNOP_WW'])
            if variable == 'T_sensor':
                var[idx_unlimited_dim]=(newdata['TSensor'])
            if variable == 'sig_laser':
                var[idx_unlimited_dim]=(newdata['SigLaser'])
            if variable == 'state_sensor':
                var[idx_unlimited_dim]=(newdata['SensorState'])
            if variable == 'V_sensor':
                var[idx_unlimited_dim]=(newdata['V_Sensor'])
            if variable == 'I_heating':
                var[idx_unlimited_dim]=(newdata['I_Heat'])
            if variable == 'error_code':
                var[idx_unlimited_dim]=(newdata['ErrorCode'])

    else:
        ncfile = NCDataset(ncfilename,'w', format='NETCDF3_CLASSIC')
        ncfile.createDimension('time',None)
        ncfile.createDimension('diameter',32)
        ncfile.createDimension('velocity',32)
        ncfile.createDimension('nv',2)


        if newdata['StationName'] == 'CABAUW':
            newdata['StationName'] = 'Cabauw'
        if newdata['StationName'] == 'KRAUTHAUSN':
            newdata['StationName'] = 'Krauthausen'
        if newdata['StationName'] == 'LEIPZIG':
            newdata['StationName'] = 'Leipzig'
        if newdata['StationName'] == 'MELPITZ':
            newdata['StationName'] = 'Melpitz'
        if newdata['StationName'] == 'LIMASSOL':
            newdata['StationName'] = 'Limassol'
        if newdata['StationName'] == 'PUNTA':
            newdata['StationName'] = 'Punta Arenas'
    

        now=datetime.datetime.now()
        data_telegram='echo -en "CS/M/S/%19;%20;%21;%09;%22;%23;%25;%13;%16;%17;%18;%10BREAK%01;%02;%03;%04;%07;%08;%12;%11;%24;%34BREAK%93;BREAK%90;BREAK%91;BREAK,\\r\\n" > /dev/ttyUSB0'
        #1-d Variables as global attributes:
        setattr(ncfile,'Title','LACROS disdrometer data')
        setattr(ncfile,'Institution','Leibniz Institute for Tropospheric Research (TROPOS), Leipzig, Germany.')
        setattr(ncfile,'Contact_person','Patric Seifert, seifert@tropos.de')
        setattr(ncfile,'Source','OTT Parsivel-2 optical disdrometer')
        setattr(ncfile,'History','Data acquired with python script parsivel2nc.py')
        setattr(ncfile,'Data_telegram_setting',data_telegram)
        setattr(ncfile,'Dependencies','external')
        setattr(ncfile,'Conventions','CF-1.6 where applicable')
        setattr(ncfile,'Processing_date',now.strftime("%Y-%m-%d, %H:%M:%S"))
        setattr(ncfile,'Author','Patric Seifert, seifert@tropos.de')
        setattr(ncfile,'Comments','Manual of the OTT Parsivel-2 can be found online at http://www.ott.com')
        setattr(ncfile,'Licence','For non-commercial use only. Any usage of the data should be reported to the contact person.')
        setattr(ncfile,'Station_Name', newdata['StationName'])
        #setattr(ncfile,'Station_ID',   newdata['StationID'])
        setattr(ncfile,'Sensor_ID',    newdata['SensorID'])
        setattr(ncfile,'Date', newdata['date'])


        #Actual Data
        data=ncfile.createVariable('lat','d',())
        setattr(data, 'standard_name','latitude')
        setattr(data,'long_name','Latitude of instrument location')
        setattr(data,'units','degrees_north')
        data.assignValue(newdata['latitude'])

        data=ncfile.createVariable('lon','d',())
        setattr(data, 'standard_name','longitude')
        setattr(data,'long_name','Longitude of instrument location')
        setattr(data,'units','degrees_east')
        data.assignValue(newdata['longitude'])

        data=ncfile.createVariable('zsl','d',())
        setattr(data, 'standard_name','altitude')
        setattr(data,'long_name','Altitude of instrument sensor above mean sea level')
        setattr(data,'units','m')
        data.assignValue(newdata['altitude'])

        data=ncfile.createVariable('time','i',('time',))
        setattr(data, 'standard_name','time')
        setattr(data,'long_name','Unix time at start of data transfer in seconds after 00:00 UTC on 1/1/1970')
        setattr(data,'units','seconds since 1970-01-01 00:00:00')
        setattr(data,'bounds','time_bnds')
        setattr(data,'comment','Time on data acquisition pc at initialization of serial connection to Parsivel.')
        data[0]=(newdata['UnixTime'])


        data=ncfile.createVariable('time_bnds','i',('time','nv'))
        setattr(data,'units','s')
        setattr(data,'comment','Upper and lower bounds of measurement interval.')
        data[0,:]=(newdata['UnixTime_bnds'][0][:])

        data=ncfile.createVariable('interval','i',('time',))
        setattr(data,'long_name','Length of measurement interval')
        setattr(data,'units','s')
        setattr(data,'comment','Variable 09 - Sample interval between two data retrieval requests.')
        data[0]=(newdata['Interval'])

        data=ncfile.createVariable('diameter','d',('diameter',))
        setattr(data,'long_name','Center diameter of precipitation particles')
        setattr(data,'units','m')
        setattr(data,'comment','Predefined diameter classes. Note the variable bin size.')
        data[:]=(newdata['diameter'])

        data=ncfile.createVariable('diameter_spread','d',('diameter',))
        setattr(data,'long_name','Width of diameter interval')
        setattr(data,'units','m')
        setattr(data,'comment','Bin size of each diameter class.')
        data[:]=(newdata['diameter_spread'])

        data=ncfile.createVariable('diameter_bnds','i',('diameter','nv'))
        setattr(data,'units','m')
        setattr(data,'comment','Upper and lower bounds of diameter interval.')
        data[:,:]=(newdata['diameter_bnds'])

        data=ncfile.createVariable('velocity','d',('velocity',))
        setattr(data,'long_name','Center fall velocity of precipitation particles')
        setattr(data,'units','m s-1')
        setattr(data,'comment','Predefined velocity classes. Note the variable bin size.')
        data[:]=(newdata['velocity'])

        data=ncfile.createVariable('velocity_spread','d',('velocity',))
        setattr(data,'long_name','Width of velocity interval')
        setattr(data,'units','m')
        setattr(data,'comment','Bin size of each velocity interval.')
        data[:]=(newdata['velocity_spread'])

        data=ncfile.createVariable('velocity_bnds','d',('velocity','nv'))
        setattr(data,'comment','Upper and lower bounds of velocity interval.')
        data[:,:]=(newdata['velocity_bnds'])

        data=ncfile.createVariable('data_raw','d',('time','diameter','velocity',), fill_value=-999.)
        setattr(data,'long_name','Raw Data as a function of particle diameter and velocity')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 93 - Raw data.')
        data[0,:,:]=(newdata['RawData'])

        data=ncfile.createVariable('number_concentration','d',('time','diameter',), fill_value=-999.)
        setattr(data,'long_name','Number of particles per diameter class')
        setattr(data,'units','log10(m-3 mm-1)')
        setattr(data,'comment','Variable 90 - Field N (d)')
        data[0,:]=(newdata['N_Field'])

        data=ncfile.createVariable('fall_velocity','d',('time','diameter',), fill_value=-999.)
        setattr(data,'long_name','Average velocity of each diameter class')
        setattr(data,'units','m s-1')
        setattr(data,'comment','Variable 91 - Field v (d)')
        data[0,:]=(newdata['V_Field'])

        data=ncfile.createVariable('n_particles','i',('time',))
        setattr(data,'long_name','Number of particles in time interval')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 11 - Number of detected particles')
        data[0]=(newdata['NParticles'])
                
        ''' No Parsivel-Times are stored yet
        data=ncfile.createVariable('Sys_Time','l',('times',))
        setattr(data,'long_name','unix time of the parsivel system in seconds after 00:00 UTC on 1/1/1970')
        setattr(data,'units','s')
        data[0]=(newdata['SysTime'])

        data=ncfile.createVariable('Sensor_Time','l',('times',))
        setattr(data,'long_name','unix time of the parsivel sensor in seconds after 00:00 UTC on 1/1/1970')
        setattr(data,'units','s')
        data[0]=(newdata['SensorTime'])
        '''

        data=ncfile.createVariable('rainfall_rate','d',('time',), fill_value=-999.)
        setattr(data,'standard_name','rainfall_rate')
        setattr(data,'long_name','Precipitation rate')
        setattr(data,'units','m s-1')
        setattr(data,'comment','Variable 01 - Rain intensity (32 bit) 0000.000')
        data[0]=(newdata['RR_Intense'])
                
        #data=ncfile.createVariable('precipitation_amount','d',('time',))
        #setattr(data,'standard_name','precipitation_amount')
        #setattr(data,'long_name','Accumulated precipitation during measurement interval')
        #setattr(data,'units','kg m-2')
        #data[0]=(newdata['RR_accum'])        

        #data=ncfile.createVariable('RR_Total','d',('time',))
        #setattr(data,'long_name','Total precipitation since start of sensor')
        #setattr(data,'units','mm')
        #data[0]=(newdata['RR_total'])
        
        data=ncfile.createVariable('radar_reflectivity','d',('time',), fill_value=-999)
        setattr(data,'standard_name','equivalent_reflectivity_factor')
        setattr(data,'long_name','equivalent radar reflectivity factor')
        setattr(data,'units','dBZ')
        setattr(data,'comment','Variable 07 - Radar reflectivity (32 bit).')
        data[0]=(newdata['dBZ'])

        data=ncfile.createVariable('E_kin','d',('time',), fill_value=-999.)
        setattr(data,'long_name','Kinetic energy of the hydrometeors')
        setattr(data,'units','kJ')
        setattr(data,'comment','Variable 24 - kinetic Energy of hydrometeors.')
        data[0]=(newdata['E_kin'])

        data=ncfile.createVariable('visibility','i',('time',), fill_value=-999)
        setattr(data,'long_name','Visibility range in precipitation after MOR')
        setattr(data,'units','m')
        setattr(data,'comment','Variable 08 - MOR visibility in the precipitation.')
        data[0]=(newdata['MOR'])

        data=ncfile.createVariable('synop_WaWa','i',('time',), fill_value=-999)
        setattr(data,'long_name','Synop Code WaWa')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 03 - Weather code according to SYNOP wawa Table 4680.')
        data[0]=(newdata['SYNOP_WaWa'])

        data=ncfile.createVariable('synop_WW','i',('time',), fill_value=-999)
        setattr(data,'long_name','Synop Code WW')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 04 - Weather code according to SYNOP ww Table 4677.')
        data[0]=(newdata['SYNOP_WW'])
                
        data=ncfile.createVariable('T_sensor','i',('time',), fill_value=-999)
        setattr(data,'long_name','Temperature in the sensor')
        setattr(data,'units','K')
        setattr(data,'comment','Variable 12 - Temperature in the Sensor')
        data[0]=(newdata['TSensor'])
                
        data=ncfile.createVariable('sig_laser','i',('time',))
        setattr(data,'long_name','Signal amplitude of the laser')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 10 - Signal ambplitude of the laser strip')
        data[0]=(newdata['SigLaser'])
                
        data=ncfile.createVariable('state_sensor','i',('time',))
        setattr(data,'long_name','State of the Sensor')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 18 - Sensor status: 0: Everything is okay. 1: Dirty but measurement possible. 2: No measurement possible.')
        data[0]=(newdata['SensorState'])
        
        data=ncfile.createVariable('V_sensor','d',('time',))
        setattr(data,'long_name','Sensor Voltage')
        setattr(data,'units','V')
        setattr(data,'comment','Variable 17 - Power supply voltage in the sensor.')
        data[0]=(newdata['V_Sensor'])

        data=ncfile.createVariable('I_heating','d',('time',))
        setattr(data,'long_name','Heating Current')
        setattr(data,'units','A')
        setattr(data,'comment','Variable 16 - Current through the heating system.')
        data[0]=(newdata['I_Heat'])

        data=ncfile.createVariable('error_code','i',('time',))
        setattr(data,'long_name','Error Code')
        setattr(data,'units','1')
        setattr(data,'comment','Variable 25 - Error code.')
        data[0]=(newdata['ErrorCode'])

    ncfile.close()
    print('***SUCCESS writing nc data! ')


############################
#ACTUAL START OF PROGRAM
############################
##History:
##20160312: optimized netcdf format, to make it most compatible for HDCP2 and to netcdf standards
##standard data telegram setting:
##echo -en "CS/M/S/%19;%20;%21;%09;%22;%23;%25;%13;%16;%17;%18;%10BREAK%01;%02;%03;%04;%07;%08;%12;%11;%24;%34BREAK%93;BREAK%90;BREAK%91;BREAK,\r\n" > /dev/ttyUSB0

#
##
###
####
#####
#######
######## USER DEFINED PART ##############

#Cabauw
##station='CABAUW' # Name set in Disdrometer: echo -en "CS/K/CABAUW\r\n" > /dev/ttyUSB0
#latitude=51.971;
#longitude=4.927;
#altitude=2.3; #including 3 m height above ground of sensor

#Krauthausen
#station='KRAUTHAUSN' # Name set in Disdrometer: echo -en "CS/K/KRAUTHAUSEN\r\n" > /dev/ttyUSB0
#latitude=50.8797;
#longitude=6.4145;
#altitude=99.;#including 3 m height above ground of sensor

#Leipzig
station='LEIPZIG'# Name set in Disdrometer:  echo -en "CS/K/LEIPZIG\r\n" > /dev/ttyUSB0
latitude=51.35312
longitude=12.43442
altitude=125. #122 m asl + 3 m height of sensor

#Limassol
#station='LIMASSOL'# Name set in Disdrometer:  echo -en "CS/K/LIMASSOL\r\n" > /dev/ttyUSB0
#latitude=34.677
#longitude=33.038
#altitude=13. 

#Melpitz
#station='MELPITZ'# Name set in Disdrometer:  echo -en "CS/K/MELPITZ\r\n" > /dev/ttyUSB0
#latitude=51.52544;
#longitude=12.92771;
#altitude=87.; #including 3 m height above ground of sensor

#Punta Arenas
station='PUNTA'# Name set in Disdrometer:  echo -en "CS/K/PUNTA\r\n" > /dev/ttyUSB0
latitude=-53.1346
longitude=-70.8834
altitude=12. #9 m asl + 3 m height of sensor

rootfolder='/home/disdrometer/data/'
#rootfolder='/home/parsivel/playground/'

######## END OF USER-DEFINED PART ##########
#######
######
####
###
##
#

#define serial port
ser = serial.Serial(port='/dev/ttyUSB0',baudrate=19200,timeout=5)
#open seerial port
#ser.open()
#print setting for serial port
#print ser

#write command to serial port
#read output from serial port
UnixTime=time.time()
#output=ser.readline(eol=',')
#ser.write("CS/P\r")
ser.write(str.encode("CS/P\r"))
ser.write(b"CS/P\r")
output=ser.readline()
#sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
#output = sio.readline()
ser.close()
#Serial connection is closed now

output=output.decode().split('BREAK')
#print output


data={}
bounds=[]

data['latitude']        = latitude 
data['longitude']       = longitude
data['altitude']        = altitude
data['date']            = time.strftime("%Y%m%d")

data['UnixTime']        = UnixTime


data['diameter']        = [0.062,0.187,0.312,0.437,0.562,0.687,0.812,0.937,1.062,1.187,1.375,
                           1.625,1.875,2.125,2.375,2.750,3.250,3.750,4.250,4.750,5.500,6.500,
                           7.500,8.500,9.500,11.000,13.000,15.000,17.000,19.000,21.500,24.500]

data['diameter_spread'] = [0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,
                           0.250,0.250,0.250,0.250,0.250,0.5,0.5,0.5,0.5,0.5,1.,1.,1.,1.,1.,
                           2.,2.,2.,2.,2.,3.,3.]

data['diameter_bnds']=[]
for i in range(len(data['diameter'])):
    data['diameter'][i]=data['diameter'][i]*1e-3
    data['diameter_spread'][i]=data['diameter_spread'][i]*1e-3
    data['diameter_bnds'].append([ data['diameter'][i]-data['diameter_spread'][i]/2, data['diameter'][i]+data['diameter_spread'][i]/2])

data['diameter_bnds'][0][0]=0.;


data['velocity']        = [0.05,0.15,0.23,0.35,0.45,0.55,0.65,0.75,0.85,0.95,1.1,1.3,1.5,1.7,
                           1.9,2.2,2.6,3.0,3.4,3.8,4.4,5.2,6.0,6.8,7.6,8.8,10.4,12.0,13.6,15.2,
                           17.6,20.8]
data['velocity_spread'] = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.2,0.2,0.2,0.2,0.2,
                           0.4,0.4,0.4,0.4,0.4,0.8,0.8,0.8,0.8,0.8,1.6,1.6,1.6,1.6,1.6,
                           3.2,3.2]
data['velocity_bnds']=[]
for i in range(len(data['velocity'])):
        data['velocity_bnds'].append([ data['velocity'][i]-data['velocity_spread'][i]/2, data['velocity'][i]+data['velocity_spread'][i]/2])




#Sensorstatus und Zeitinfos
parts=output[0].split(';')

#print output
#Times from Parsivel are not used yet
#Instead, Unix time of the computer is used
#data['Timestamp']   = parts[0]        # %19: Zeitstempel Beginn der Messung
#data['SensorTime']  = parts[1]        # %20: Zeit im Sensor
#data['SensorDate']  = parts[2]        # %21: Datum im Sensor
#

data['UnixTime_bnds']=[]
data['Interval']    = int(parts[3])  # %09: Messinterval s
data['UnixTime_bnds'].append([data['UnixTime']-data['Interval'], data['UnixTime']])
data['StationName'] = parts[4]        # %22: Stationsname
data['StationID']   = parts[5]        # %23: Stationsnummer
data['ErrorCode']   = int(parts[6])   # %25: Fehlercode
data['SensorID']    = parts[7]        # %13: Seriennummer des Sensors
data['I_Heat']      = float(parts[8]) # %16: Heating Current
data['V_Sensor']    = float(parts[9]) # %17: Sensor Voltage
data['SensorState'] = int(parts[10])  # %18: Sensorstatus
data['SigLaser']    = int(parts[11]) # %10: Signalamplitude vom Laser

#Messwerte
parts=output[1].split(';')
data['RR_Intense']  = float(parts[0])/3600./1000. # %01: mm/h converted to m/s
data['RR_total']    = float(parts[1]) # %02: mm
data['SYNOP_WaWa']  = int(parts[2])   # %03: Synop WaWa
data['SYNOP_WW']    = int(parts[3])   # %04: Synop WaWa
data['dBZ']         = float(parts[4]) # %07: Radar Reflectivity
data['MOR']         = int(parts[5])   # %08: Sichtweite im Niederschlag nach MOR
data['TSensor']     = int(parts[6])+273 # %12: Sensor Temperature degC converted to K
data['NParticles']  = int(parts[7])  # %11: Anzahl der detektierten Partikel
data['RR_accum']    = float(parts[8]) # %24: Regenmenge absolut
data['E_kin']       = float(parts[9]) # %34: Kinetische Energie

#prepare 32x32-bin Rawdata Array
RawData = output[2].split(';')
RawData = ToLong(RawData)

a = asarray(RawData)
a = a.reshape(32,32)
data['RawData'] = a.tolist()

#prepare 32-bin N_Field Array
N_Field         = output[3].split(';')
data['N_Field'] = ToFloat(N_Field)

#prepare 32-bin V_Field Array
V_Field         = output[4].split(';')
data['V_Field'] = ToFloat(V_Field)

#Call function to write nc data
write_nc(rootfolder,data)
