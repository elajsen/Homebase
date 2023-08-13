# Homebase

# Set up config
You need to set up a config file with the username and passwords for your applications. You need to create a file called: credentials.conf. The config file should look like this:

{
    "bbva": {
        "username": "username",
        "password": "password"
    },
    "basic-fit": {
        "username": "username",
        "password": "password"
    },
    "orange": {
        "username": "username",
        "password": "password"
    },
    "mongo": {
        "username": "route to the mongoDB"
    }
}

# Host
To launch the site you need to enter the same folder as the manage.py script. You need to be inside of a EC2 machine and then run:
python3 manage.py runserver 0.0.0.0:8000

The 0.0.0.0 will then bind to the public IP of the EC2. 

You need to configure the IP addresses, both incoming and outgoing. You have to do this both inside of the EC2 machine and on the cloud page of the MongoDB
