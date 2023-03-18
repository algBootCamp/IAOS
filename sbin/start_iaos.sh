#!/bin/sh

scriptname=$0
targetdir=$(echo $scriptname | awk -F 'sbin' '{print $(NF-1)}')
app="app"
targetdir=$targetdir$app
cd $targetdir
#echo $targetdir

startdir=$(pwd | awk -F / '{print $NF}')
#echo $startdir
if [ "$startdir" == "sbin" ]; then
  echo "Automatic Go To Project Folder To Finish The Job"
  cd ../app
  sh ../sbin/control start
  exit 0
elif [ "$startdir" = "app" ]; then
  echo "Right Target Folder, Start Job Accepted"
else
  echo "Please Go To Project Folder 'iaos-server/app' And Retry, Exit!"
  exit 1
fi

if [ -d "../logs/gunicornlog" ]; then
  rm -rf ../logs/gunicornlog/*
fi

sh ../sbin/control start
