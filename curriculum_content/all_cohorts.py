#!/usr/bin/env python
# coding: utf-8

# combine all of the command line parameters into one big file of cohort stats

import json
import pandas as pd

import os


from pathlib import Path

import sys


    
def combine(institutions):
    print("Combining " + " ".join(institutions))
    all_filename = "all_cohorts.csv"

# from https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist        
    Path(all_filename).unlink(missing_ok=True)
    
    key_fields = ['institution', 'Cohort', 'AcademicYearStart', 'Women3', 'Men3', 'MaxElectives']

    all_cohorts = []

    try:

        for instutition in institutions:
            cohorts_df = pd.read_csv(os.path.join(institution, ""))
            cohorts_df['institution']
            all_cohorts.append(electives_df)
        all_electives_df = pd.concat(all_electives, ignore_index=True)

        all_electives_df.to_csv(all_filename, index=False)
        print ("Total of " + str(len(all_electives_df.index)) + " electives saved to " + all_filename )
    except OSError as err:
        print("OS error:", err)

def main():
    try:
        args = sys.argv[1:]
        combine(args)
    except IndexError:
        print("No input files defined on command line")
        return

if __name__ == "__main__":
    main()
