## counting-book
This service merges in HBAS download counts from non-CDN repos with the CDN repos, and creates summaries and total counts for the HBAS repos.

It does not actually download any log file data, and expects them to be set up in advance.

Specifically, it creates these two files:
- https://wiiubru.com/history/totals_Switch.json
- https://wiiubru.com/history/totals_WiiU.json

As well as lighter weight individual files for each package / daily counts:
- https://wiiubru.com/history/output_Switch/vgedit.json
- https://wiiubru.com/history/output_WiiU/vgedit.json

### Requirements
- `output.json` file existing non-CDN download counts
  - (this was the previous stats file used by the web frontend)
- `pullzone-logs` folder from CDN anonymized log archives

### License
MIT License
