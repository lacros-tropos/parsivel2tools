#!/bin/bash
set -x
today=`date +"%Y%m%d%H%M"`
yyyymmddYesterday=`date -d "-1 day" +"%Y%m%d"`
yyyymmYesterday=`date -d "-1 day" +"%Y%m"` 
yyyymmddToday=`date +"%Y%m%d"`
yyyymmToday=`date +"%Y%m"`
hour=`date +"%H"`

# Parse command-line arguments
while [ $# -gt 0 ]; do
    if [ $1 = "--date" ]; then
        if [ $# -lt 2 ]; then
            echo "No date given"
            exit 1
        fi
        yyyymmddToday=$2
	yyyymmToday=$(echo ${yyyymmddToday} | cut -c1-6)
        shift
        shift
    else
        echo "Error: \"$1\" not understood"
        exit 1
    fi
done

cd /home/disdrometer/python
python plot_disdrometer.py -s ${yyyymmddToday}0000 -e ${yyyymmddToday}2359
mkdir -p /home/disdrometer/png/$yyyymmToday
cd /home/disdrometer/tmp
/usr/bin/montage -border 0 -geometry 800x -quality 19 -tile 1x6  rainfall_rate.png acc_precip.png n_particles.png radar_reflectivity.png  number_concentration.png  fall_velocity.png /home/disdrometer/png/${yyyymmToday}/${yyyymmddToday}_disdrometer.png

#at the beginning of a new day also replot yesterdays' data
if [ $hour -lt 2  ]; then
 cd /home/disdrometer/python
 python plot_disdrometer.py -s ${yyyymmddYesterday}0000 -e ${yyyymmddYesterday}2359
 mkdir -p /home/disdrometer/png/$yyyymmYesterday
 cd /home/disdrometer/tmp
 /usr/bin/montage -border 0 -geometry 800x -quality 19 -tile 1x6  rainfall_rate.png acc_precip.png n_particles.png radar_reflectivity.png  number_concentration.png  fall_velocity.png /home/disdrometer/png/${yyyymm}/${yyyymmddYesterday}_disdrometer.png
fi

