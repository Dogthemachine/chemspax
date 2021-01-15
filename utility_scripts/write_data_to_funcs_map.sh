#!/usr/bin/env bash
# script to use in combination with functionalize_and_optimize_x.sh, those recursive approaches generate a
# ${skeleton}_funcs_map.csv file, here all the information per functionalization is stored.
# This script can find newly calculated data for that functionalization and add it in a new column to the
# ${skeleton}_funcs_map.csv file. In this way it is possible to have each functionalization as a row and all the necessary
# data as a column

echo ""
echo "---------------------------------------------------------------------------------------------"
echo "Looks like you want to add some data to a functionalization you did."
echo "Created by: Adarsh Kalikadien & Vivek Sinha"
echo "---------------------------------------------------------------------------------------------"

# name for the new column of data to be added
DATA_NAME=$1
CSV_FILES=`ls *funcs_map.csv`

if [ -z "$1" ]
  then
    echo "No column name for the new data supplied"
    echo "This was a test to see if you actually checked the script for its correctness"
    exit 1
fi


for CSV_FILE in ${CSV_FILES}; do
# make .bak file to save as backup if something went wrong
cp ${CSV_FILE} ${CSV_FILE}.bak
N=`wc -l ${CSV_FILE} | cut -d' ' -f 1`
# add the new column index
INDEX_NAMES=`sed "1q;d" ${CSV_FILE}`
NEW_INDEX_NAMES=${INDEX_NAMES},${DATA_NAME}
sed "1s/$INDEX_NAMES/$NEW_INDEX_NAMES/" ${CSV_FILE} > ${CSV_FILE}_new
mv ${CSV_FILE}_new ${CSV_FILE}
    for i in `seq 1 ${N}`; do
    # first column of ${skeleton}_funcs_map.csv is the filename of the functionalization
    filename=`sed "${i}q;d" ${CSV_FILE} | cut -d',' -f 1`
    # script supposes that everything is in its own separate directory
    if [[ -d "${filename}" ]]
        then
        # put command to get the data in $DATA variable
        DATA=`grep "Co" ${filename}/scr.complex/mullpop | awk -F '  +' '{print $10}'` # get spin density
        #DATA=`calculate_rmsd ${filename}/xyzfile1 ${filename}/xyzfile2` # get RMSD
        #DATA=`get_gaussian_info.py ${filename}/logfile ${filename}/${filename}.csv && sed "2q;d" ${filename}/${filename}.csv | cut -d',' -f 4` $ field 4 for E and field 10 for G from DFT .log
        # add new data on correct line
        OLD_LINE=`sed "${i}q;d" ${CSV_FILE}`
        NEW_LINE=${OLD_LINE},${DATA}
        sed "${i}s/${OLD_LINE}/${NEW_LINE}/" ${CSV_FILE} > ${CSV_FILE}_new
        mv ${CSV_FILE}_new ${CSV_FILE}
    else
        echo ${filename} is not a directory
    fi
    done
done