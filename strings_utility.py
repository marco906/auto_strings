#!/usr/bin/python3
import chardet
import codecs
import os
import os.path
import re

format_encoding = 'UTF-16'
filePath = os.path.dirname(__file__)

def readTranslations(fileName):
	if not os.path.exists(fileName):
		print(" ... no file found, returning empty translation %s" % (fileName))
		return []

	stringset = []
	f = _getFileContent(filename=fileName)
	if f.startswith(u'\ufeff'):
		f = f.lstrip(u'\ufeff')
	cp = r'(?:/\*(?P<comment>(?:[^*]|(?:\*+[^*/]))*\**)\*/)'
	p = re.compile(
		r'(?:%s[ \t]*[\n]|[\r\n]|[\r]){0,1}(?P<line>(("(?P<key>[^"\\]*(?:\\.[^"\\]*)*)")|(?P<property>\w+))\s*=\s*"(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"\s*;)' % cp,
		re.DOTALL | re.U)
	c = re.compile(r'//[^\n]*\n|/\*(?:.|[\r\n])*?\*/', re.U)
	ws = re.compile(r'\s+', re.U)
	end = 0
	start = 0
	for i in p.finditer(f):
		start = i.start('line')
		end_ = i.end()
		key = i.group('key')
		comment = i.group('comment') or ''

		if not key:
			key = i.group('property')
		
		value = i.group('value')
		while end < start:
			m = c.match(f, end, start) or ws.match(f, end, start)
			if not m or m.start() != end:
				print("Invalid syntax: %s" % f[end:start])
			end = m.end()
		end = end_
		stringset.append({'key': key, 'value': value, 'comment': comment})
	return stringset

def _getFileContent(filename, encoding='UTF-16'):
	f = open(filename, 'rb')
	try:
		content = f.read()
		if chardet.detect(content)['encoding'].startswith(format_encoding):
			encoding = format_encoding
		else:
			encoding = 'utf-8'
		f.close()
		f = codecs.open(filename, 'r', encoding=encoding)
		return f.read()
	except IOError as e:
		print("Error opening file %s with encoding %s: %s" % (filename, format_encoding, e.message))
	except Exception as e:
		print("Unhandled exception: %s" % e.message)
	finally:
		f.close()

def _createDirIfNeeded(fileName):
	if not os.path.exists(os.path.dirname(fileName)):
		os.makedirs(os.path.dirname(fileName))

def writeCommentToFile(outputDir, stringsFileName, comment, outputTargetCode):
	outputFileName = os.path.join(outputDir, outputTargetCode + os.path.join(".lproj", stringsFileName))
	_createDirIfNeeded(outputFileName)

	with open(outputFileName, "a", encoding="utf-8") as myfile:
		contentToWrite = "/* " + comment.strip() + " */\n\n"
		myfile.write(contentToWrite)

def writeTranslationToFile(outputDir, stringsFileName, key, translation, comment, outputTargetCode):
	outputFileName = os.path.join(outputDir, outputTargetCode + os.path.join(".lproj", stringsFileName))
	_createDirIfNeeded(outputFileName)

	with open(outputFileName, "a", encoding="utf-8") as myfile:
		contentToWrite = ""
		if len(comment) != 0:
			contentToWrite = "/* " + comment.strip() + " */\n"
		contentToWrite += "\"" + key + "\" = \"" + translation + "\";\n\n"
		myfile.write(contentToWrite)

def mergeTranslations(existingLines, addedLines):
	linesToAdd = []
	for addedLine in addedLines:
		isNew = True
		for i, existingLine in enumerate(existingLines):
			if addedLine["key"] == existingLine["key"]:
				existingLines[i] = addedLine
				isNew = False
				break
		if isNew:
			linesToAdd.append(addedLine)
	existingLines += linesToAdd

def clearContentsOfExportFile(destinationPath, stringsFileName, target):
	fileName = os.path.join(destinationPath, target + os.path.join(".lproj", stringsFileName))
	_createDirIfNeeded(fileName)
	open(fileName, 'w').close()

def clearContentsOfFile(outputDir, stringsFileName, target):
	fileName = os.path.join(outputDir, target + os.path.join(".lproj", stringsFileName))
	_createDirIfNeeded(fileName)
	open(fileName, 'w').close()

def cleanUpTranslation(s: str) -> str:
	f = s.replace('\\N', '\\n')
	f = f.replace('\\"', '"')
	f = f.replace("\"", "\\\"")
	f = f.replace("％", "%")
	f = f.replace("% @", "%@")
	f = f.replace("（", " (")
	f = f.replace("）", ") ")
	f = f.replace("% @", "%@")
	f = f.replace("\\ n", "\n")
	f = f.strip(' ')
	return f