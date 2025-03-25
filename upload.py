#!/usr/bin/env python3
# run this script after count.py, to update the counts back to FTP

import os, json, ftplib, json

# credentials from config.json
loaded = False
with open("config.json", "r") as file:
    config = json.load(file)
    ftpLogsHost = config["ftpLogsHost"]
    ftpLogsUsername = config["ftpLogsUsername"]
    ftpLogsPassword = config["ftpLogsPassword"]
    loaded = True

if not loaded:
    print("config.json not found or invalid")
    exit(1)

# we're going to log into the ftp server and make sure it works
ftp1 = ftplib.FTP_TLS(ftpLogsHost)
res = ftp1.login(ftpLogsUsername, ftpLogsPassword)
ftp1.prot_p()  # Switch to secure data connection
print("Logged into FTP server with TLS:", ftpLogsHost, res)

# change into history dir
ftp1.cwd("/history")

# upload the totals files
for platform in ["Switch", "WiiU"]:
    with open(f"totals_{platform}.json", "rb") as file:
        ftp1.storbinary(f"STOR totals_{platform}.json", file)
        print("Uploaded", f"totals_{platform}.json")
    # upload each package json
    ftp1.cwd(f"/history/output_{platform}") # assume it exists already
    for package in os.listdir(f"output_{platform}"):
        if package.endswith(".json"):
            with open(f"output_{platform}/{package}", "rb") as file:
                ftp1.storbinary(f"STOR {package}", file)
                print("Uploaded", package)