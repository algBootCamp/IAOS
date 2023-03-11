#!/bin/sh

scriptname=$0
targetdir=`echo $scriptname | awk -F 'sbin' '{print $(NF-1)}'`
app="app"
targetdir=$targetdir$app
cd $targetdir
#echo $targetdir

startdir=`pwd | awk -F / '{print $NF}'`
if [ "$startdir" == "sbin" ];then 
    echo "Automatic Go To Project Folder To Finish The Job"
    cd cd ../app
    sh ../sbin/control stop
    exit 0
elif [ "$startdir" = "app"  ]; then
    echo "Right Target Folder, Stop Job Accepted"
else
    echo "Please Go To Project Folder 'iaos-server/app' And Retry, Exit!"
    exit 1
fi 
sh ../sbin/control stop
