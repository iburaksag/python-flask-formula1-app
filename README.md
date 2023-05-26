# Python Flask Formula1 App

> #python #flask #googlecloud #appengine #datastore #firebase #html #css #bootstrap

In this assignment I built a PaaS application which will be a database that stores information about F1 drivers and teams. I had required to deal with users who login and logout. This will function a little like Wikipedia in that anyone who is logged in can change anything, anyone who is logged out can change nothing.<br><br>
In this application users should be able to add and update drivers and teams that are in the database. They should also be able to perform comparisons of either teams or drivers. Also, some filtering actions has been implemented. With filtering however you will be limited on the types of queries you can perform due to the NoSQL nature of the database. Please check the Assignment folder for more details.<br><br>
In this project, you need to use firebase for authentication purposes. This will keep track of user/password combinations. 
For setting up Firebase, check out the link:
https://console.firebase.google.com/u/0/

## Getting Started 🏁

First before we can start with anything we will need to create a python virtual environment as we will need to install things into it without messing with the local python environment. In the project directory, you can run:

### `python3 -m venv env`

After this we will need to run the following command:

### `source env/bin/activate`

Make sure you have created your environment and sourced it as shown above and run the following command:

### `pip install -r requirements.txt`

Before you go to run this project you will need the JSON file nearby to access the datastore. Before you run your application in your command line you will need to set the session variable GOOGLE_APPLICATION_CREDENTIALS with the location of this JSON file.

### `export GOOGLE_APPLICATION_CREDENTIALS=”../app-engine-3-testing.json”`

Run your application by executing the following command:
 
### `python main.py`

