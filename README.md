# DISCLAIMER!
This code is purely for personal use, developed as a hobby/utility for myself. This has no official sanction by ICICIdirect or ICICI Securities, and they bear no responsibility for any bugs, failures, or issues in this code.

# USAGE
## Purpose
While downloading historical data over long peropds of time, we need to write a loop. This loop must also be mindful of weekends and holidays in order to be efficient. And most such loops are repetitive, with small changes. With the availability of PySimpleGUI it became possible to automate this task to a large extent. Later versions will also have futures and option chain downloading, as well as a permanent database to avoid duplication.

## To use:
1. Download the breeze_downloader.py into the folder where you want to store the data
2. Run file
3. Give your credentials and click connect
4. Once connnected, go to second tab and enter contract details and from- and to- date
5. Click validate to do a sanity check
6. If valid, click download and wait for it to finish

## How it works
1. gets ^NSEI/NIFTY50 1day data from Yahoo! Finance for a reference list of dates
2. batches the list of dates into lengths long enough to fetch in a single call
3. truncates the list of list of dates into start- and end- dates
4. fetches data in a loop, appending to a temporary list
5. list of fetched data is converted to a pandas dataframe which is saved as a csv in the same folder as the breeze_downloader.py file

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
