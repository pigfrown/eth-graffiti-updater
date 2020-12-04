# prysm-grafiti-updater

Automatically updates prysm grafiti tag when a block is found.

Watches prysm-validator systemd logs for successful block proposals. When seen edits the validator service with the new grafiti line and restarts the service.


