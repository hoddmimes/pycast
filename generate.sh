#!/bin/bash
rm ./msg/generated/* 2>> /dev/null
java -jar ./libs/pymessage-1.0.jar -xml ./xml/NetMsgFileSet.xml
