
Visuals the pedestrian counts on Bahnhofstrasse for 12 months (Oct-22 to Sept-23)

Setup steps (based on MacOS)  


Step 1:  checkout the git repo from github to your local machine using the following command in a terminal window:

   git clone git@github.com:pgfox/bahnhofstrasse_visual.git

step 2: create a python virtual enviroment to run the code. 

    cd bahnhofstrasse_visual
    python3 -m venv $PWD/venv

step 3: activate the virtual environment and install all the needed python packages in the virtual env:

    source venv/bin/activate
    pip install -r requirements.txt

step 4: invoke the python main line file from the terminal (with virtual env activated):

   python3 Bahnhofstrasse.py


