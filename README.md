## Behavior Data Processing

This Python script processes behavior data from Excel files. It's useful for researchers who need to analyze large amounts of behavior data. The script merges duplicate rows, updates observation IDs, calculates total and mean durations for each behavior, and exports the processed data to new Excel files.

## Installation

Before running the script, you need to install the required Python packages. You can do this by running the following command in your terminal:

`pip install -r requirements.txt`

## Usage

1. Place your Excel files in a directory named InputSheets in the same directory as the Python script.
2. Run the script by executing the following command in your terminal:
`python behavior_data_processing.py`
3. The script will process the data and save the output to new Excel files in a directory named OutputSheets.

Please note that the script expects the Excel files to be in a specific format. Make sure your files have the correct format before running the script.