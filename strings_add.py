#!/usr/bin/python3
import argparse
import os.path
import re

from strings_utility import readTranslations, clearContentsOfExportFile, exportTranslationToFile

parser = argparse.ArgumentParser()
parser.add_argument("-s", default="output", help="path to source localization files")
parser.add_argument("-d", default="./", help="path to target folder in your project where the strings should be inserted")
parser.add_argument("-f", default="Localizable.strings", help="file name of the .strings file")
args = parser.parse_args()

filePath = os.path.dirname(__file__)
sourceResourcePath = os.path.join(filePath, args.s.strip())
destinationResourcePath = os.path.expanduser(args.d.strip())
stringsFileName = args.f.strip()

supportedLanguageCodes = []

l = os.path.join(filePath, "LanguageCodes.txt")
with open(l, 'r') as supportedLangCodeFile:
	for line in supportedLangCodeFile:
		if line.strip().startswith("#"):
			continue
		
		langArray = line.split()
		translateFriendlyName = langArray[0]
		googleTranslateTargetCode = langArray[1]
		deeplTranslateTargetCode = langArray[2]
		outputTargetCode = langArray[3]

		supportedLanguageCodes.append(outputTargetCode)

for dirpath, dirnames, filenames in os.walk(sourceResourcePath):
	for dirname in dirnames:
		if dirname.find(".lproj") != -1:
			dirLang = dirname.split(os.path.sep)[-1].replace(".lproj", "")

			if dirLang in supportedLanguageCodes:
				localizablePath = os.path.join(os.path.join(dirpath, dirname), stringsFileName)
				if not os.path.exists(localizablePath):
					print("Error source path not found: %s" % (localizablePath))
					continue

				print("Reading source path: %s" % (localizablePath))
				sourceLines = readTranslations(localizablePath)
				numSource = len(sourceLines)
				print("Found %a translations in source path: %s" % (numSource,localizablePath))
				if numSource == 0:
					continue
				
				destinationLocalizablePath = os.path.join(os.path.join(destinationResourcePath, dirname), stringsFileName)

				if not os.path.exists(localizablePath):
					print("Error destination path not found: %s" % (destinationLocalizablePath))
					continue

				print("Reading destination path: %s" % (destinationLocalizablePath))
				destinationLines = readTranslations(destinationLocalizablePath)
				print("Found %a translations in destination path: %s" % (len(destinationLines),destinationLocalizablePath))

				destinationLines += sourceLines

				clearContentsOfExportFile(destinationResourcePath, stringsFileName, dirLang)

				for line in sorted(destinationLines, key = lambda i: str(i['key']).lower()):
					stringName = line['key']
					stringVal = line['value']
					stringComment = line['comment']

					if not stringComment:
						stringComment = ""

					stringVal = re.sub("\.([A-Z])", "\. \\1", stringVal)

					exportTranslationToFile(destinationResourcePath, stringsFileName, stringName, stringVal, stringComment, dirLang)
