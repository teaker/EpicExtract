import PyPDF2
import re
import os
import glob
from pathlib import Path
import fitz
from io import FileIO
import pandas as pd
from pathlib import Path


print("This application will extract all flowsheet data from\n"
      "an UNABRIDGED Epic record and will save each entry to\n"
      "an Excel spreadsheet.\n"
      "NOTE:  This app is not perfect and may not accurately\n"
      "extract all data (e.g. where flowsheet data is split\n"
      "across two pages.)\n"
      "\n")

inputFile = Path(input("Enter full path to Unabridged PDF file: ")) #Ask user for the file
outputFile = Path(input("Enter full path for Excel spreadsheet to save to\n"
                        "(e.g.:  C:\output.xlsx)    : ")) #Ask user for the file
object = fitz.open(inputFile)
NumPages = object.pageCount
flowsheets = {}
byreg = re.compile(r"[-][A-Z][A-Z]\s[a][t]")
rownameregex = re.compile(r"[R][o][w]\s[N][a][m][e]")

for i in range(0, NumPages):
    lastCatIndex = 0
    PageObj = object[i]
    Text = PageObj.getText()
    TextDictBlocks = PageObj.getTextBlocks()
    BlocksOnly = [x[4] for x in TextDictBlocks]
    pdfpage = i + 1

    if rownameregex.search(Text):
        #splits and saves separately to keys in dict
        for block in TextDictBlocks:
            if 56 <= block[0] <= 59:
                vital = str(block[4].split('\n')[0])
                if vital not in flowsheets:
                    flowsheets[vital] = []

        for index, block in enumerate(TextDictBlocks):
            if 56 <= block[0] <= 59:
                vital = block[4].split('\n')
                #for i in range(1, len(vital)):
                #    flowsheets[vital[0]].append(vital[i])
                for i in range(1, (len(vital) - 1)):
                    if vital[i] != ' —' and byreg.search(vital[i]) == None and byreg.search(vital[i + 1]) != None:
                        #print(str(index) + vital[i] + " = " + vital[i + 1])
                        flowsheets[vital[0]].append(vital[i] + " | " + vital[i + 1] + " | " + "Page " + str(pdfpage))
                lastCatIndex = index
            elif block[0] >= 100:
                vital = block[4].split('\n')
                vitalCat = TextDictBlocks[lastCatIndex][4].split('\n')[0]
                for i in range(0, (len(vital) - 1)):
                    if vital[i] != ' —' and byreg.search(vital[i]) == None and byreg.search(vital[i + 1]) != None:
                        #print("NONfirst" + str(index) + vital[i] + " = " + vital[i + 1])
                        flowsheets[vitalCat].append(vital[i] + " | " + vital[i + 1] + " | " + "Page " + str(pdfpage))


empty_keys = [k for k,v in flowsheets.items() if not v]
for k in empty_keys:
    del flowsheets[k]

keys = []
entries = []

for key, values in flowsheets.items():
    for value in values:
        entries.append(key + "|" + value)

#df = pd.DataFrame.from_dict(flowsheets, orient='index')
#df.to_excel("D:/pdfScratchFile/outtie4.xlsx")

entries2 = [i.split('|') for i in entries]
df2 = pd.DataFrame(entries2)
df2.to_excel(outputFile)
print("Finished.  File saved to " + str(outputFile))