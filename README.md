# To run
To install the fbchat dependency:
```bash
$ sudo apt-get install python-pip
$ sudo pip install fbchat
```

From the same directory as the script run:
```bash
$ FB_USER=<USER> FB_PASS=<PASS> FB_DEFAULT_GROUP=<GROUP_ID> ./messengerbot.py
```

# Commands
  - Basics
    - `boto help` - Links to this README file.
    - `boto echo MESSAGE` - Replies with the message.
    - `boto tell MESSAGE` - Sends the message to the default group.
  - Images
    - `boto kitteh` - Replies with a random cute cat.
    - `boto kitteh bomb` - Replies with several random cute cats.
    - `boto pug me` - Replies with a random pug.
    - `boto pug bomb` - Replies with several random pugs.
    - `boto rocket` - Replies with a random rocket.
    - `boto rocket man` - Replies with a random rocket man.
  - Points
    - `boto +NUM THING` - Gives NUM points to THING. THING can have spaces.
    - `boto -NUM THING` - Takes NUM points away from THING. THING can have spaces.
    - `boto points` - Displays all current points.
    - `boto forget about SOME PHRASE` - Removes SOME PHRASE from the points record.
  
# Enviornment variables
  - `FB_USER` - The username to login with.
  - `FB_PASS` - The password to login with.
  - `FB_DEFAULT_GROUP` - The id of the default group to send messages with `boto tell`
