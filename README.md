# Translate
Auto translate `.strings` localization files into multiple languages for use in an XCode project.

# Usage
1. Add keys and translations in the origin language in a `.strings` file
2. `pip3 install googletrans==4.0.0-rc1` for Google Translate
3. `pip3 install --upgrade deepl` for DeepL
4. `python3 strings_translate.py`
```
usage: strings_translate.py [-h] [-t T] [-a A] [-f F] [-o O] [-v V]

optional arguments:
  -h, --help  show this help message
  -t T        set translation service. Possible values: deepl, google (default). For DeepL an api key must be provided with -a
  -a A        set DeepL api token
  -f F        set the path to the origin .strings file to read keys and base translations from, default is Localizable.strings
  -o O        set the language that is used in the origin .strings file, default is english
  -v V        Verbose
```

**NOTE**: Failed translations are not copied over to the output directory.

## how to specify a custom path to the .strings file
`python3 strings_translate.py -f /some/path/to/Localizable.strings`

## how to use DeepL translator
To use DeepL you need to set the translation service to deepl and add you DeepL api token

`python3 strings_translate.py -t deepl -a AUTH_TOKEN_HERE`

## how to set origin languge
use `-o` to set your origin language,

for example `python3 strings_translate.py -o de` when your base translations are in German,

by default the origin language is set to english

## how to add or remove languages
edit `LanguageCodes.txt` to add or remove languages you want to translate. Make sure to use the correct language codes for each service.

## Add translated strings to project
After translating your strings, you can add them to your existing XCode project. The new strings will be inserted to your existing localzation files.
`python3 strings_add.py -d /some/path/to/project/`

```
usage: strings_add.py [-h] [-s S] [-d D] [-f F]

optional arguments:
  -h, --help  show this help message and exit
  -s S        path to source localization files, default is output
  -d D        path to target folder in your project where the strings should be inserted
  -f F        file name of the .strings file, default is Localizable.strings
```

**NOTE**: Currently there is no check if a key already exists.
