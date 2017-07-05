#!/usr/bin/python

#1 run shell script or commands to get latest 10 log from HGLog.log
#1.1 make into a file or just put into a variable will be decided later
#2 read into variables or map so we can compare values of 'Leave'
#3 Find highest one and send to DataDog agent
#5 optional if 'Leave' is abnormaly high, then send it to our emails directly

import subprocess
import datetime
import time

#A line from current HGLog.log
#2016-02-16 20:16:22, INFO, Total: 4303000, Leave: 15


def main():
    #A variable for how many last lines from HGLog.log
    lastLog = 10

    #Path for HGLog.log
    pathForHGLog = "/home/issuser/gateway/obdlog/HGLog.log"

    #Path for saving a log that we create for DataDog
    pathForSavingLog = "/var/log/"
    
    #Combining into one file(today; ex: hglogForDataDog.log.01012016"
    #Previously:
    #cmd = "cat " + pathForSavingLog + "hglogForDataDog.log >> " + pathForSavingLog + "hglogForDataDog.log" + "." + time.strftime("%m%d%Y")
    tmpStr = []
    tmpStr.append('cat ')
    tmpStr.append(pathForSavingLog)
    tmpStr.append('hglogForDataDog.log >> ')
    tmpStr.append(pathForSavingLog)
    tmpStr.append('hglogForDataDog.log.')
    tmpStr.append(time.strftime("%m%d%Y"))
    tmpStr.append(' 2> /dev/null')
    cmd = "".join(str(x) for x in tmpStr)
    subprocess.Popen(cmd, shell=True)
    
    #remove previous log file
    #Previously:
    #cmd = "rm " + pathForSavingLog + "hglogForDataDog.log"
    tmpStr = []
    tmpStr.append('rm ')
    tmpStr.append(pathForSavingLog)
    tmpStr.append('hglogForDataDog.log')
    tmpStr.append(' 2> /dev/null')
    cmd = "".join(str(x) for x in tmpStr)  
    subprocess.Popen(cmd, shell=True)
    
    #get last a few 'Leave' numbers from HGLog.log
    #Previously:
    #cmd = "cat "+ pathForHGLog +"|grep Leave| tail -" + str(lastLog)
    tmpStr = []
    tmpStr.append('cat ')
    tmpStr.append(pathForHGLog)
    tmpStr.append('|grep Leave| tail -')
    tmpStr.append(str(lastLog))
    cmd = "".join(str(x) for x in tmpStr)     
    outputVar = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]

    #For Testing:
    #tmpTes tStr = '2016-02-16 20:16:22, INFO, Total: 4303000, Leave: 75\n2016-02-16 20:16:22, INFO, Total: 4303000, Leave: 115\n2016-02-16 20:16:22, INFO, Total: 4303000, Leave: 15\n2016-02-16 20:16:22, INFO, Total: 4303000, Leave: 55'
    #parse_hglog(tmpTestStr)
    
    resultLog = parse_hglog(outputVar)
    logFile = open(pathForSavingLog + "hglogForDataDog.log", "w")
    logFile.write(resultLog)
    logFile.close()    


def parse_hglog(output):
    i = 0
    done = 0    
    nextStartingPoint = 0
    newLineEndingPoint = -1    
  
    dateTimeStr=[]
    metricCategory=[]
    totalJobs=[]
    leaveValues=[]
    
    while not done:
        dateTimeStr.append(i)
        metricCategory.append(i)
        totalJobs.append(i)
        leaveValues.append(i)
        newLineEndingPoint = output.find('\n', nextStartingPoint)
        if newLineEndingPoint == -1:
            done = 1
        else:
            newLineStr = output[nextStartingPoint:newLineEndingPoint].rstrip()
            tmpDateTimeStr, tmpMetricCategory, tmpTotalJobs, tmpLeaveValues = newLineStr.split(',')
            dateTimeStr[i] = tmpDateTimeStr
            metricCategory[i] = tmpMetricCategory
            totalJobs[i] = tmpTotalJobs
            tmpStr, tmpValue = tmpLeaveValues.split(':')
            leaveValues[i] = int(tmpValue.strip())
            newLineEndingPoint = newLineEndingPoint - 1
            nextStartingPoint = newLineEndingPoint + 2
            i+=1
    #Try to find a largest no.
    indexOfLargest = -1
    largestNo = -1
    index=0
    for i in leaveValues:
        if i >= largestNo:
           indexOfLargest = index
           largestNo = i
        index+=1
    timeStamp = time.mktime(datetime.datetime.strptime(dateTimeStr[indexOfLargest], "%Y-%m-%d %H:%M:%S").timetuple())
    leaveResult = 'gateway.leaves' + ' ' + str(timeStamp) + ' ' + str(largestNo) + ' ' + 'metric_type=counter unit=leave' +'\n'
    return leaveResult

main()