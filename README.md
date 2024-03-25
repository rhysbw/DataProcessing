## Behavior Data Processing

This Python script processes behavior data from Excel files. It's useful for researchers who need to analyze large amounts of behavior data. The script merges duplicate rows, updates observation IDs, calculates total and mean durations for each behavior, and exports the processed data to new Excel files.

## Usage (on MacOS you may need to use python3 instead of python in the commands bellow)

1. Create a New Folder/Directory (called anything)
2. Download the files `behavior_data_processing.py` and `requirements.txt` (to that folder)
4. Place your Excel files in a directory named InputSheets in the same directory as the Python script. It should look as follows:
![image](https://github.com/rhysbw/DataProcessing/assets/93877064/87a565aa-5dae-462a-a81e-c36285216ee8)
5.  Open CMD/Terminal and Navigate to the New Folder you created in step 1
    1.  type `cd `
    2.  drag and drop the New Folder you created in step 1 into the CMD window
    3.  hit enter
6. Run:
 `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`
7.  Run the script by executing the following command in your terminal:
`python behavior_data_processing.py`
8. The script will process the data and save the output to new Excel files in a directory named OutputSheets.

Please note that the script expects the Excel files to be in a specific format. Make sure your files have the correct format before running the script.
