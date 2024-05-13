# Location-Extraction-From-URLs
"Location Extraction From URLs" is a repository focused on extracting geographical information from URLs. This project provides a tool  to parse URLs and identify relevant location data, aiding in applications that use large db formed from web scraping.
# Install

For running this program I've used:

```
python==3.11.9
```

Dependencies needed for this program can be seen also in the requirments.txt file but here they are:

```
beautifulsoup4==4.12.3
langdetect==1.0.9
ollama==0.2.0
pandas==2.2.2
Requests==2.31.0
requests_html==0.10.0
translate==3.6.1
lxml_html_clean==0.1.1
geocoder==1.38.1
```
Use command `pip install -r requirements.txt`

Ollama model used is llama3

Run command
```
ollama pull llama3
```

# Usage
The main file `location_extracion.py` will acompany us with this text in terminal

```
usage: location_extraction.py [-h] [-m MAX_URLS] csv_file
location_extraction.py: error: the following arguments are required: csv_file
```

For example, using the program in this case we'll need to run the comand

```
python3 location_extraction.py random_100.csv -m 0
```

For crawling more urls within the given url as the input we ca also change the command to any other number that 0 or give `-m MAX_URLS`
With the command on 0 the program will crawl for internal urls only on the webpage given as input 

The csv file runned also for the test can be found in the `Testing_Random_100_urls` folder where it takes as input the main db converted from `snappy.parquet` to `csv` from the folder `Database_Conversion`

Both folder having a `py` file for conversion and extracting randomly 100 urls for a fair short test of this program

# How it works 
In summary the program it is parsing trought the `db` excepting errors `detects` the website langauge for further translation of necessary keywords which they are stored into `translated_words` variable since the websites crawled can be in any language. Afterwards we are retriving only the important urls crawled with the help of the keywords for better efficency which are then given to `olamma` running `llama3 model` where afterwards the result are stored into the variable `assistant_response` where further filtering si done and also for the desired format of the output is checked and adjusted with the help of `geolocator` from the `location variable` where is after stored the final output in the `output_locations.txt`. From this output if the response has `OK` into it that means that the final address is a correct one otherwise it is specified with `Location not found!`

# Testing
For a random selection of 100 urls these are the results given:

<img width="606" alt="Screenshot 2024-05-13 at 04 25 35" src="https://github.com/Albu2103/Location-Extraction-From-URLs/assets/167569646/ef68fed4-d034-4dc5-baeb-21aa862a26cf">

The output can be seen in the `output_locations.txt` file 

# Challenges
There is no `NLP` library specialized for location identifying since there is a vast option of postal addresses. The most relaible one being `LocationTagger` which extracts only `Country`, `Region` and `City` where for this case the entire physical address it is needed with high accuracy. Local llm used for this project can bemisleading at times thus further filtering of information and adding additional libaries like `geolocator` it is necessary. Substitute to `geolocator`, `geopy` does not work accordingly to the task since most of the addresses do not work for enhancing them, using `latitude` and `longitude` did help but gives for the approximate location address.
