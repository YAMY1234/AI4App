# README

## Extract_program_name
extract_program_name is a Python script designed to extract program names and their corresponding URLs from a NEU_demo.json file. The results are then stored in an Excel file, `program_url_pair.xlsx`. The script is intended for researchers or developers who need to extract specific information from JSON data.

### Working Principle
The script initially extracts all program words from the "program-wordBank.xlsx" file and then searches for these words in the "NEU_demo.json" file. If a program name is found, it attempts to locate a URL within the same JSON object. If a program name and URL are found within the same object, the pair is saved. If a program name is found without a corresponding URL in the same object, the script continues searching for a URL in the higher-level JSON object.

## Extract_useful_link
Extract_useful_link is a Python script that extracts useful links related to each program from the program's main page, which are stored in `program_url_pair.xlsx'. The useful links are then stored in an Excel file, program_useful_link.xlsx.

### Working Principle
The script reads the 'program_url_pair.xlsx' and uses requests to send HTTP request to each URL. It then uses BeautifulSoup to parse the HTML of the web page. The script extracts useful links by searching for a tags in the parsed HTML, and matches the link text with the contents of 'url_bank.xlsx' to decide whether the link is useful.

## Extract_program_details
Extract_program_details is a Python script that, for each program, extracts details including deadlines, GPA requirements, TOEFL and IELTS scores, interview requirement, and essay requirements. The results are stored in program_details.xlsx.

### Working Principle
The script reads the 'program_useful_link.xlsx' file, and for each program, it sends HTTP requests to each useful link. It uses BeautifulSoup to parse the HTML of the page, and then uses a variety of methods (including regular expressions) to extract the necessary information from the parsed HTML. This information is then stored in the program_details.xlsx file.
