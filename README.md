# DISCLAIMER!
This code is purely for personal use, developed as a hobby/utility for myself. This has no official sanction by ICICIdirect or ICICI Securities, and they bear no responsibility for any bugs, failures, or issues in this code.

# breeze_helper
Historical data downloader for ICICIdirect's Breeze API

# AIMS
1. DONE: A continuous downloader to download large amounts of data given Breeze's limitation of 1000 lines of data per request, and store everything in a single CSV file. NOTE: 1000 has been hard-coded into this script, so in case of future changes, it should be updated.
2. TODO: Replace CSV with an sqlite database
3. TODO: Recursively download one futures series
4. TODO: Recursively download an entire option chain for a give expiry

# DEPENDENCIES:
Some dependecies are not used in entirety, and I am too lazy to edit the list:
* import PySimpleGUI as sg
* from datetime import date
* from breeze_connect import BreezeConnect
* from io import BytesIO
* from zipfile import ZipFile
* from urllib.request import urlopen
* import pandas as pd
* from datetime import datetime
* from os import getcwd, name
* from dateparser import parse
* import yfinance as yf
* from itertools import batched
