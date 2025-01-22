#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/22 10:50
# @Author  : Yu.Jingkai
# @File    : date_map.py
import json
from datetime import datetime, timedelta

# Set the date range
date_range_st = "20240107"
date_range_ed = "20240331"

matrix_abs_path = "../matrix_results/0107-0331_new/matrix_abs.json"
date_map_path = "../matrix_results/0107-0331_new/date_map.json"

# Initialize the date map
date_map = {}

# Open and read the matrix_abs.json file
with open(matrix_abs_path, "r") as file:
    for line in file:
        try:
            # Parse the line into a json object
            json_obj = json.loads(line)

            # Check if the json object has the required fields
            if "start_date" in json_obj and "end_date" in json_obj and "timestamp" in json_obj:
                start_date = datetime.strptime(str(json_obj["start_date"]), "%Y%m%d")  # Convert start_date to datetime
                end_date = datetime.strptime(str(json_obj["end_date"]), "%Y%m%d")  # Convert end_date to datetime

                # Check if the difference between start_date and end_date is 7 days
                if (end_date - start_date).days == 6:
                    # Check if the end_date is within the date range
                    if date_range_st <= end_date.strftime("%Y%m%d") <= date_range_ed:
                        date_map[end_date.strftime("%Y%m%d")] = json_obj["timestamp"]
        except json.JSONDecodeError:
            # Skip the line if it cannot be parsed into a json object
            continue

# Write the date map to the date_map.json file
with open(date_map_path, "w") as file:
    for key in sorted(date_map.keys()):
        json.dump({key: date_map[key]}, file)
        file.write('\n')
