# Production of netcdf files from serially transferred Parsivel2 data stream
- Within the script 'parsivel2nc.py' update the user-specific info accordingly for the new site
- Add the correct station name for the current site to the disdrometer settings. The below command works in case your Parsivel2 is connected via USB0 interface: `echo -en "CS/K/Leipzig\r\n" > /dev/ttyUSB0 `
- Set the standard data transfer telegram so that data can be interpreted with parsivel2nc.py script:
`echo -en "CS/M/S/%19;%20;%21;%09;%22;%23;%25;%13;%16;%17;%18;%10BREAK%01;%02;%03;%04;%07;%08;%12;%11;%24;%34BREAK%93;BREAK%90;BREAK%91;BREAK,\r\n" > /dev/ttyUSB0`
- The data acquisition script parsivel2nc.py is automatically run every 30 seconds via a cronjob applied to the bash script  `get_parsivel_data.sh`
- Adjust `get_parsivel_data.sh` to your system settings 
 
# Netcdf file structure produced by parsivel2nc.py
- See the file `netcdf_structure.txt` to see how the ncdump output of the parsivel2 netcdf files look like
- The processing of the netcdf files (for plotting) is demonstrated in `plot_disdrometer.py`

# Plotting of main disdrometer data
- Plotting of the netcdf files created with parsivel2nc.py can be realized using the function `plot_disdrometer.py`. Check the file and adjust it to your system settings, before usage. 
