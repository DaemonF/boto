# To run
From the same directory as the script run:
```
FB_USER=<USER> FB_PASS=<PASS> FB_DEFAULT_GROUP=<GROUP_ID> ./messengerbot.py
```

# Commands
  - `boto echo MESSAGE` - Replies with the message.
  - `boto tell MESSAGE` - Sends the message to the default group.
  - `boto kitteh` - Replies with a random cute cat.
  - `boto pug me` - Replies with a random pug.
  
# Enviornment variables
  - `FB_USER` - The username to login with.
  - `FB_PASS` - The password to login with.
  - `FB_DEFAULT_GROUP` - The id of the default group to send messages with `boto tell`
