import sys, os, operator

file = "test.txt"

newFile = open("new.txt", "w")

with open(file) as f:
    line = f.readline()

    count = 5001
    change = 3593

    while line:
        num = line.split(' ')
        if str(num[0]) == str(count):

            newString = str(change) + line[len(str(count)):]
            newFile.write(newString + "\n")
            change += 1
            count += 1
            
        line = f.readline()