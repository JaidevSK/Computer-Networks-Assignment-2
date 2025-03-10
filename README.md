# Computer Networks Assignment 2

## Environment Setup

Ensure that Python3, conda and Wireshark are installed on the device

Create a new conda environment and install the following libraries using the command

`pip install <library_name>`

The required libraries are:
- mininet
- dpkt
- numpy
- matplotlib
- pandas
- datetime
- tqdm

Activate the environment using `conda activate environment_name`

## Q1
To run question one, run the file Q1_main using the command 

`sudo python3 Q1_main.py --option = a/b/c/d`
 
If this doen not run, we can also run the individual files using the command 

`sudo python3 Q1a.py`, `sudo python3 Q1b.py`, `sudo python3 Q1c.py`, `sudo python3 Q1d.py`

The configurations can then be given as user inputs, as given on the terminal.

Between consecutive runs, make sure to run the following command `sudo mn --clean`.

Once the commands are run, the results will be obtained in pcap format in the respective folders. To further analyse them, open them using wireshark OR analyse them using the pcap analyser file called Q1_PCAP_Analyser.py after updating the folder addresses on lines 182, 183 and 184.

The results will be obtained in the corresponding folders.

## Q2
In order to run this question, run the files Q2 and Q2_Mitigated. The commands to be used are:
- `sudo python3 Q2.py`
- `sudo python3 Q2_Mitigated.py`

Once these are run, the corresponding pcap files will be obtained. To analyse them, update the paths in the files Q2_IOPlotter and Q2_Analyser and run them.
- `python3 Q2_IOPlotter.py`
- `python3 Q2_Mitigated.py`

## Q3
To run this question, execute the command:

`bash Q3_main.sh`

If there are any errors, run the files Q3_client.py and Q3_server.py simultaneoulsy in the terminal. If the configuartion has to be changed, change the parameter values in the top part of Q3_client.py file.