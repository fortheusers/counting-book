## counting-book
This service merges in HBAS download counts from non-CDN repos with the CDN repos, and creates summaries and total counts for the HBAS repos.

It also has helper scripts to download and upload these counts to/from the servers.

Specifically, it creates these two files:
- https://wiiubru.com/history/totals_Switch.json
- https://wiiubru.com/history/totals_WiiU.json

As well as lighter weight individual files for each package / daily counts:
- https://wiiubru.com/history/output_Switch/vgedit.json
- https://wiiubru.com/history/output_WiiU/vgedit.json

### Usage
First, edit API keys as necessary into `config.json`, credentials are needed for both non-CDN and CDN endpoints.

Run `fetch.py` to set up the following files:
- `output.json` file existing non-CDN download counts
  - this is the still-being-updated stats file for all non-CDN hits
- `pullzone-logs` folder from CDN anonymized log archives
  - only modified files will be redownloaded, and these contain cache hit/miss info

After those files are present, run `count.py` to generate the stats counts. It will create:
- `output_{platform}` - A folder of `{package}.json` files representing stats for just that package, across all time
- `totals_{platform}.json` - An overview of total counts for each package

Then, `upload.py` can be ran to send these stats the their storage endpoint again, which will be reflected on [hb-app.store/stats](https://hb-app.store/stats?apps=wiiu/vgedit,switch/vgedit) immediately.

Magnezone and repogen will pull these stat totals in on their next refresh. This repo does not perform the actual refresh on those repos, and leaves it to them to pull in the latest numbers.

### License
MIT License
