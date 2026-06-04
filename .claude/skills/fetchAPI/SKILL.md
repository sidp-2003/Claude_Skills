- - - 
name: fetchAPI
description: Fetches data from API and handles responses. Use when interacting with external API or retrieving data from web services.
- - - 

## Usage

### Step-1 : Fetch data from APIs
You need to make python API calls to fetch data from following URLs using async httpx:
["https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_customer.csv","https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_store.csv","https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_date.csv","https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_product.csv","https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_sales.csv","https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_returns.csv"]


### step-2: Handle API responses
After fetching a data you need to create a directory having name with current date in YYYY-MM-DD format and save the fetched data as CSV file in that directory. The location of he directory should be ".claude/skills/fetchAPI/data".

### step-3: Logging
You need to create a log directory at ".claude/skills/fetchAPI/logs" with name current data and time in the format "YYYY-MM-DD-HH-MM-SS" and save a log file in that directory with the name "fetchAPI.log". The log file should contain information about the API calls made, including what APis called, what were successful and what were not,encountered during the process.


