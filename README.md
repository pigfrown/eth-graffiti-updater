# eth-graffiti-updater

Automatically updates graffiti when a block is found.

Until prysm adds the ability to update the graffiti tag, this script can be used to change graffiti everytime a block is found. It can (maybe) be used with other clients.

To work with other clients search in validator logs and find a string that is printed _only_ when a block is found, and launch with the --search-for option set to that string.

Requires that the validator is running as a systemd service!

## How it works

Read in a file containing the of graffiti lines we want to add, in order, to the blockchain.

Each line must be equal to or less than 32 bytes

Poll the systemd journal for the prysmvalidator service until a block is submitted. 

When a block has been submitted, update (by default) /tmp/graffiti with the new graffiti.

Restart the systemd service to use the new graffiti.

## How to use

Run ```python update_graffiti.py --help``` to get full list of options.

For basic usage:

Modify your existing or create a new systemd service.
This service should read the contents of (by default) /tmp/graffiti into the GRAFFITI environment variable, and then use this variable to populate the value of the --graffiti field.
Example service file has been included in the repo, but will need adjusting to work with your setup (paths etc). 
Make sure validator is launched with ```bash -c```

Create a text file which contains your required graffiti lines, in order.. In this example we'll call this file "mygraffiti"

Become root with ```sudo su```

Run the script with ```python update_graffiti.py mygraffiti```

You can check the script is working by checking the contents of /tmp/graffiti (should be the first line of your input file) and checking how your validator was launched with ```pgrep -a validator```. You should see your graffiti line in the output. If you can't see your graffiti check service file is launching with the validator with ```bash -c```


## Bugs
Not escaping properly in the systemd service which could lead to unexpected results if graffiti lines contain quotes or bash syntax characters like && etc

## Security Issues

Anyone with write access to /tmp/graffiti can fuck up your shit.

Probably more.

## TODO

Better subprocess/systemctl restart error checking

Add "search_for" as a cmd line flag for use with other clients

Proper handling/escaping of input lines

Better error handling/messages. E.g. when file is not found. Permissions not valid.

Allow non-root usage/document how to do this.

