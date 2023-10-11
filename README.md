# Delta X Labeling Software

## Description

The IMIU Image Labeling Software and its associated Python Server enable efficient data labeling for AI training. Labeled data produced by this software can be seamlessly integrated with AIX training applications, streamlining the machine learning process.

## Installation Instructions

### Download/Clone this repository

Clone or download this repository to access the Delta X Labeling Software and Python Server code.

### Enviroment preparation

* The server code is written in Python, so ensure that the Python environment is installed on your machine. If it's not already installed, you can refer to the official Python website at https://www.python.org/downloads/.
* After installing Python, you need to install the necessary Python libraries listed in the `requirements.txt` file by command `pip install -r requirements.txt`.

### Run server.py file

* Check your device IP adress and paste it in line 971 of `server.py` file. You can do this by go to the `Network and Internet Settings` of your computer and check the IPv4 address. Copy it and replace to the default IP address at line 971.
* Run the `server.py` file.

### Launch the IMIU software

* Run the software in `imiu_software` folder.

