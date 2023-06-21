#!/usr/bin/env python
# coding: utf-8

# take the input file (electives_in.csv) and the column definitions given in institution.json
# create electives_pre.csv, which contains the same data but in a standard format
# on the command line take the institution name as a parameter e.g. Durham_England

import json
import pandas as pd

import os

import pprint

import sys

def heading(field):
    return "<h2>" + field + "</h2>"
    
def wrangle(institution_name):
    institution_json = "institution.json"

    print("Wrangling elective module information for" + institution_name)

    pp = pprint.PrettyPrinter(indent=4)

    key_fields = ['institution', 'elective', 'overview']
    overview_fields = ['title', 'summary', 'content', 'ilo']
    all_fields = key_fields + overview_fields

    try:
        path = institution_name

        with open(os.path.join(path, institution_json)) as institution_file:
            institution_config = json.load(institution_file)
            pp.pprint(institution_config)
        electives_df = pd.DataFrame(columns=all_fields, dtype="string")

        pre_scraped = institution_config.get('pre_scraped_file',"")
        if not pre_scraped:
            print ("Could not wrangle the module information for " + institution_name + ": no input file defined in " + institution_json)
            return
        
        fields = institution_config.get('fields', "")
        pre_scraped_df = pd.read_csv(os.path.join(path, pre_scraped), dtype='str')
        pre_scraped_df['institution'] = institution_name
        pre_scraped_df['overview'] = ""
        for field in [i for i in all_fields if i not in ['institution','overview']]:
            lookup = fields[field]
            if not lookup:
                pre_scraped_df[field] = ""
                continue
            pre_scraped_df[field] = pre_scraped_df[lookup]

            if field in overview_fields:
                pre_scraped_df['overview'] =  pre_scraped_df['overview'] + heading(field) + pre_scraped_df[field]

        electives_df = pre_scraped_df[all_fields]
        electives_df = electives_df[electives_df['elective'].str.len() >0]
        electives_df.to_csv(os.path.join(path,'electives_pre.csv'), index= False)
    except OSError as err:
        print("OS error:", err)

def main():
    try:
        arg = sys.argv[1]
        institution_name = arg
        wrangle(institution_name)
    except IndexError:
        print("No institution defined on command line")
        return

if __name__ == "__main__":
    main()
