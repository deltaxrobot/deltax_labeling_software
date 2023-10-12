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

![get_ip](./imgs/get_ip_address.png)

* Run the `server.py` file.

![run_server](./imgs/get_ip_address_2.png)

### Launch the IMIU software

* Run the software in `imiu_software` folder.
![run_software](./imgs/run_imiu_software.png)

## Usage Instructions

### Software Usage

#### Step 1: Change the IP address

Change the IP address to the IP address of the computer running the `server.py` file.

![Step 1](./imgs/change_ip_adress.png)

#### Step 2: Login admin account

* Log in to default admin account with username: `admin` and password: `123456`.

![Step 2](./imgs/login_admin.png)

#### Step 3: Create Project

![Step 3](./imgs/create_project.png)

#### Step 4: Upload images

![Step 4](./imgs/upload_images.png)