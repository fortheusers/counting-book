#!/usr/bin/env python3
# run this script before count.py, to download the dependencies

import os, json, ftplib, json, datetime

# credentials from config.json
loaded = False
with open("config.json", "r") as file:
    config = json.load(file)
    ftpLogsHost = config["ftpLogsHost"]
    ftpLogsUsername = config["ftpLogsUsername"]
    ftpLogsPassword = config["ftpLogsPassword"]
    cdnLogsHost = config["cdnLogsHost"]
    cdnLogsUsername = config["cdnLogsUsername"]
    cdnLogsPassword = config["cdnLogsPassword"]
    loaded = True

if not loaded:
    print("config.json not found or invalid")
    exit(1)

# # we're going to log into both ftp servers and make sure they work
ftp1 = ftplib.FTP_TLS(ftpLogsHost)
res = ftp1.login(ftpLogsUsername, ftpLogsPassword)
ftp1.prot_p()  # Switch to secure data connection
print("Logged into FTP server with TLS:", ftpLogsHost, res)

ftp2 = ftplib.FTP_TLS(cdnLogsHost)
res = ftp2.login(cdnLogsUsername, cdnLogsPassword)
ftp2.prot_p()  # Switch to secure data connection
print("Logged into CDN server with TLS:", cdnLogsHost, res)

# # download the output.json data from ftp1
ftp1.cwd("/history")
with open("output.json", "wb") as file:
    ftp1.retrbinary("RETR output.json", file.write)
print("Downloaded output.json from FTP server")

# recursively download the pullzone logs from ftp2
def ls(ftp):
    out = []
    ftp.retrlines("LIST", lambda x: out.append(x.split()[-1]))
    return out

prefix = "/4tu-data/"
ftp2.cwd(prefix + "pullzone-logs")
for platform in ls(ftp2):
    platFolder = f"pullzone-logs/{platform}"
    os.makedirs(platFolder, exist_ok=True)
    ftp2.cwd(prefix + platFolder)
    for year in ls(ftp2):
        print("Processing year:", year)
        yearFolder = platFolder + "/" + year
        ftp2.cwd(prefix + yearFolder)
        for month in ls(ftp2):
            monthFolder = yearFolder + "/" + month
            ftp2.cwd(prefix + monthFolder)
            for file in ftp2.nlst():
                os.makedirs(monthFolder, exist_ok=True)
                localPath = f"{monthFolder}/{file}"
                # if we have an existing file, check the size of the file first
                # if it's the same, skip
                if os.path.exists(localPath):
                    # also, if the expected date of this file is more htan a week ago, skip it regardless
                    date = f"{year}-{month}-{file.split('_')[0]}"
                    date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    if date < datetime.datetime.now() - datetime.timedelta(days=7):
                        print(f"Skipped {localPath} (too old)")
                        continue
                    ftp2.sendcmd(f"TYPE I")
                    remoteSize = ftp2.size(file)
                    if os.path.getsize(localPath) == remoteSize:
                        print(f"Skipped {localPath}")
                        continue
                with open(localPath, "wb") as f:
                    ftp2.retrbinary(f"RETR {file}", f.write)
                    print(f"Downloaded {localPath}")