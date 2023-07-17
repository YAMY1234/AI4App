# Scraper.py README

## Introduction
Scraper.py is a Python script designed to extract program names and their corresponding URLs from a NEU_demo.json file. The results are then stored in an Excel file, `program_url_pair.xlsx`. The script is intended for researchers or developers who need to extract specific information from JSON data.

## Dependencies
1. json: Used for reading and handling JSON files.
2. openpyxl: Used for reading from and writing to Excel files.

## Usage
1. Ensure that the `openpyxl` library is installed in your Python environment. If not, it can be installed using the following command:

pip install openpyxl


2. Replace the paths of `json_file` and `word_bank_file` in the code with your own JSON file and word bank Excel file.

3. In the terminal or command prompt, navigate to the folder containing `scraper.py`, and run the following command:

python scraper.py

4. After the script finishes running, a `program_url_pair.xlsx` file will be generated in the same directory. This file will contain the program names and their corresponding URLs that were extracted.

## Working Principle
The script initially extracts all program words from the "program-wordBank.xlsx" file and then searches for these words in the "NEU_demo.json" file. If a program name is found, it attempts to locate a URL within the same JSON object. If a program name and URL are found within the same object, the pair is saved. If a program name is found without a corresponding URL in the same object, the script continues searching for a URL in the higher-level JSON object.

## Notes
1. Make sure the paths and filenames for "NEU_demo.json" and "program-wordBank.xlsx" are correct.
2. Changes in the structure of the JSON file may affect the search results. You may need to adjust the code to accommodate new JSON structures.

That's the instruction and introduction for `scraper.py`. If there are any other questions or if you need to extend the functionality for specific purposes, feel free to contact.