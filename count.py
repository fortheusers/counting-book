#!/usr/bin/env python3
import json, os, gzip, datetime
from collections import Counter, defaultdict

platforms = ["Switch", "WiiU"]

# currently requires manually downloading pullzone logs from the CDN
# as well as the output.json from the current history system

for platform in platforms:
    dailyCounts = defaultdict(lambda: Counter()) # mapping of package name -> dictionary of date -> count
    # load in the existing historical counts
    with open("output.json", "r") as file:
        data = json.load(file)
        dailyCounts.update(data[platform])
        # convert each package's value froma dictionary to a counter
        for package in dailyCounts:
            dailyCounts[package] = Counter(dailyCounts[package])

    # for each gz file, process the log lines for each zip file HIT
    folder = f"pullzone-logs/hbas-{platform.lower()}"
    for path, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".gzip"):
                # if we already have a summary, load it and use it
                if os.path.exists(f"{path}/{file}_summary.json"):
                    with open(f"{path}/{file}_summary.json", "r") as f:
                        countSummary = json.load(f)
                        for package in countSummary:
                            dailyCounts[package] += Counter(countSummary[package])
                        print(f"Loaded {file}_summary.json")
                    continue
                # same as our dailyCounts, but for this specific file
                countSummary = defaultdict(lambda: Counter())
                with gzip.open(os.path.join(path, file), "rt") as f:
                    for line in f:
                        line = line.strip().split("|")
                        # skip if it's not a HIT
                        if line[0] != "HIT":
                            continue
                        # skip if it's not a 200 response
                        if line[1] != "200":
                            continue

                        timestamp = line[2]
                        remote_file = os.path.basename(line[7])
                        user_agent = line[9]

                        # skip if not zip
                        if not remote_file.endswith(".zip"):
                            continue
                        remote_file = remote_file[:-4] # remove .zip
                            
                        isConsole = user_agent == "-" or user_agent.startswith("HBAS/")

                        # convert timestamp from unix string to dd/MMM/yyyy string
                        timestamp = int(timestamp) // 1000
                        timestamp = datetime.datetime.utcfromtimestamp(timestamp).strftime("%d/%b/%Y")
                        
                        # now merge these counts with our existing counts
                        countSummary[remote_file][timestamp] += 1

                # write this out as a cache for next time
                with open(f"{path}/{file}_summary.json", "w") as f:
                    json.dump(countSummary, f, indent=4)
                # merge these counts with our dailyCounts
                for package in countSummary:
                    dailyCounts[package] += countSummary[package]
                print(f"Processed {file}, saved {file}_summary.json")

    # save the final updated counts
    with open("output2.json", "w") as file:
        data[platform] = dailyCounts
        json.dump(data, file, indent=4)
    
    # write out simple totals as well, sorted from highest to lowest
    with open(f"totals_{platform}.json", "w") as file:
        totals = []
        for package in dailyCounts:
            totals.append((sum(dailyCounts[package].values()), package))
        totals.sort(reverse=True)
        out = {}
        for count, package in totals:
            out[package] = count
        json.dump(out, file, indent=4)
    
    # save the data in a more compressed format, for each year -> month -> days
    # with a different file for each package
    os.makedirs(f"output_{platform}", exist_ok=True)
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    daysInMonth = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  
    for package in dailyCounts:
        packageData = dailyCounts[package]
        yearData = {}
        for year in range(2016, 2026):
            yearData[year] = {}
            for monthIdx in range(1, 13):
                month = months[monthIdx]
                yearData[year][month] = []
                for day in range(1, daysInMonth[monthIdx] + 1):
                    day = str(day).zfill(2)
                    key = f"{day}/{month}/{year}"
                    count = packageData[key]
                    yearData[year][month].append(count)
                # if the whole month was 0, don't bother saving it
                if sum(yearData[year][month]) == 0:
                    del yearData[year][month]
            # if the whole year was 0, don't bother saving it
            if not yearData[year]:
                del yearData[year]

        with open(f"output_{platform}/{package}.json", "w") as file:
            file.write(json.dumps(yearData, indent=4))