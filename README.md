# eth-grafiti-updater

Automatically updates graffiti when a block is found.

Designed and tested for use with Prysm. Will probably work with other clients but will need modifying slightly (search_for variable will need updating)

Until prysm adds the ability to update the graffiti tag, this script can be used to change graffiti everytime a block is found. It can (maybe) be used with other clients.

## How to use

Run ```python update_graffiti.py --help``` to get full list of options.

For basic usage:

Update/create a systemd service which will read from a file (e.g. /tmp/graffiti) to populate the graffiti flags value. See example service file. Make sure validator is launched with ```bash -c```

Create a text file which contains your required graffiti lines, in order.. In this example we'll call this file "mygraffiti"

Become root with ```sudo su```

Run the script with ```python update_graffiti.py mygraffiti```


## Assumptions:
1) prysm validator is running as a systemd service.
2) prysm validator systemd service reads from (by default) /tmp/graffiti to populate the contents of the --graffiti field (see example service)

## How it works
Read in a list of graffiti lines we want to add, in order, to the blockchain.
Each line must be equal to or less than 32 bytes
Poll the systemd journal for the prysmvalidator service until a block is submitted.  
When a block has been submitted, update (by default) /tmp/graffiti with the new graffiti.
Restart the systemd service to use the new graffiti.

## Bugs
Not escaping properly in the systemd service which could lead to unexpected results if graffiti lines contain quotes or bash syntax characters like && etc

## Security Issues

 anyone with write access to /tmp/graffiti can fuck up your shit.
 Probably more.

## TODO

Better subprocess/systemctl restart error checking
Add "search_for" as a cmd line flag for use with other clients
Proper handling/escaping of input lines
Better error handling/messages. E.g. when file is not found. Permissions not valid.
Allow non-root usage/document how to do this.



