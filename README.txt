trello_hipchat_push
-------------------

add your credentials to the environment and update the config.json file with
your trello and hipchat ids and run from the command line.  will sleep for
20 seconds between checks of trello

for convenience, update your credentials in run.sh

a file `seen.json` is created to keep track of the ids that were already pushed
to hipchat so that if you restart the service it will not flood the chat room
with messages
