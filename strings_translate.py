#!/usr/bin/python3
import argparse
import os
import os.path

import deepl
from googletrans import Translator

from strings_utility import readTranslations, writeTranslationToFile, clearContentsOfFile, cleanUpTranslation

filePath = os.path.dirname(__file__)

parser = argparse.ArgumentParser()
parser.add_argument("-t", default="google", help="set translation service. Possible values: deepl, google (default). For DeepL an api key must be provided with -a")
parser.add_argument("-a", default="", help="set api key to use for DeepL")
parser.add_argument("-f", default="Localizable.strings", help="set the path to the Localizable.strings to read keys from")
parser.add_argument("-o", default="en", help="set the origin locale for auto translation, default is english")
parser.add_argument("-d", default="output", help="set the destination path for the exported translations")
parser.add_argument("-v", default="0", help="Verbose")
args = parser.parse_args()
outputDir = str(args.d).strip()

def translateSourceText(key, sourceText, translateTargetCode):
	translatedText = sourceText

	try:
		if str(args.t).strip().lower() == "deepl":
			auth_key = str(args.a).strip()
			deeplTranslator = deepl.Translator(auth_key)
			result = deeplTranslator.translate_text(sourceText, source_lang=args.o, target_lang=translateTargetCode)

			translatedText = result.text

			if args.v == "1":
				print("  %s => %s" % (key, translatedText))
		else:
			googleTranslator = Translator()
			obj = googleTranslator.translate(sourceText, src=args.o, dest=translateTargetCode)

			translatedText = obj.text

			if args.v == "1":
				print("  %s => %s" % (key, translatedText))
	except Exception as e:
		print("\n  ..... !! FAILED !! to translate for %s: %s = %s\n" % (translateTargetCode, key, e))

		return (sourceText, False, False)

	translatedText = cleanUpTranslation(translatedText)

	totalFormattersInSource = sourceText.count('%')
	totalFormattersInOutput = translatedText.count('%')

	formatterFailed = False
	if totalFormattersInSource != totalFormattersInOutput:
		formatterFailed = True
		print("\n  ..... !! WARNING !! Formatters don't match in: %s => %s (lang: %s)\n" % (sourceText, translatedText, translateTargetCode))
	elif translatedText.count('% ') != sourceText.count('% '):
		formatterFailed = True
		print("\n  ..... !! WARNING !! Formatters have an invalid space: %s => %s (lang: %s)\n" % (
		sourceText, translatedText, translateTargetCode))
	
	if translatedText.find('%') != -1 and translatedText[translatedText.find('%') + 1] not in ['u', 'l', '@', 'f', '1', '2', '3', 'd', '.']:
		formatterFailed = True

		print("\n  ..... !! WARNING !! Invalid formatter: %s => %s (lang: %s)\n" % (
		sourceText, translatedText, translateTargetCode))

	return (translatedText, True, formatterFailed)

def translateLineInFile(translationTuple, translateTargetCode, outputTargetCode):
	stringName = translationTuple['key']
	sourceText = translationTuple['value']
	stringComment = translationTuple['comment']

	if not stringComment:
		stringComment = ""
	
	(translation, success, warning) = translateSourceText(stringName, sourceText, translateTargetCode)

	if success:
		writeTranslationToFile(outputDir, stringsFileName, stringName, translation, stringComment, outputTargetCode)
			
	return (success, warning)

def translateFile(stringsFileName, languageName, translateTargetCode, outputTargetCode):
	print(languageName)

	clearContentsOfFile(outputDir, stringsFileName, outputTargetCode)

	totalLinesTranslated = 0
	totalLinesNeeded = 0
	totalWarnings = 0
	for translationTuple in originLines:
		totalLinesNeeded += 1
		(success, warning) = translateLineInFile(translationTuple, translateTargetCode, outputTargetCode)
		if success:
			totalLinesTranslated += 1
		if warning:
			totalWarnings += 1

	if totalWarnings != 0:
		print("ERROR: CHECK WARNINGS. Total reported %s" % (totalWarnings))
	
	if totalLinesNeeded != totalLinesTranslated:
		print("ERROR: NOT ALL LINES TRANSLATED. Total lines translated for %s: %s. Original source count: %s" % (languageName, totalLinesTranslated, totalLinesNeeded))
	else:
		print("✅ Lines translated for %s: %s" % (languageName, totalLinesTranslated))

if str(args.t).strip().lower() == "deepl":
	print("Using DeepL translator")

originPath = args.f.strip()
dirName, stringsFileName = os.path.split(originPath)
print("Reading source language: %s" % (originPath))

originLines = readTranslations(originPath)

print("Total lines in source: %s\n" % (len(originLines)))
p = os.path.join(filePath, 'LanguageCodes.txt')
with open(p, 'r') as supportedLangCodeFile:
	for targetLine in supportedLangCodeFile:

		if targetLine.strip().startswith("#"):
			continue
		
		targetArray = targetLine.split()
		languageName = targetArray[0]
		languageCodeGoogle = targetArray[1]
		langageCodeDeepl = targetArray[2]
		outputTargetCode = targetArray[3]

		languageCode = langageCodeDeepl if str(args.t).strip().lower() == "deepl" else languageCodeGoogle
		
		translateFile(stringsFileName, languageName, languageCode, outputTargetCode)

		print("\n")

