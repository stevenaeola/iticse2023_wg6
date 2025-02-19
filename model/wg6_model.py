# Run stan model to estimate parameters on WG6 data
import pandas as pd
import numpy as np
import os
import json

from cmdstanpy import CmdStanModel
import arviz as az

import argparse

from sklearn import preprocessing




parser = argparse.ArgumentParser(description='Load WG6 elective curriculum and enrolment data and use STAN model to extract parameters.')
parser.add_argument('--samples', type=int, default=500)
parser.add_argument('--seed', type=int, default=1)
parser.add_argument('--model', default='model') # defaults to type=string
args = parser.parse_args()

seed = args.seed
num_samples = args.samples
model_file = args.model

print("seed ", seed, "num_samples", num_samples)

cohorts = pd.read_csv(os.path.join("..", "enrolment", "all_cohort_enrolment_rounded.csv"))
enrolments = pd.read_csv(os.path.join("..", "enrolment", "all_elective_enrolment_rounded.csv"))
#code_set = pd.read_csv(os.path.join("..", "curriculum_content", "ACM_2023_CAH_codes.csv"), dtype="string")

le_cohort = preprocessing.LabelEncoder()
le_elective = preprocessing.LabelEncoder()

cohorts['Students3'] = cohorts['Men3'] + cohorts['Women3']
cohorts['icy'] = cohorts['institution'] + cohorts['Cohort'].astype('string')  + cohorts['AcademicYearStart'].astype('string')
cohorts['cohort_id'] = le_cohort.fit_transform(cohorts['icy'])

enrolments['icy'] = enrolments['institution'] + enrolments['Cohort'].astype('string')  + enrolments['AcademicYearStart'].astype('string')
enrolments['cohort_id'] = le_cohort.transform(enrolments['icy'])
enrolments['icym'] = enrolments['icy'] + enrolments['MCode'].astype('string')
enrolments['module_id'] = le_elective.fit_transform(enrolments['icym'])
enrolments.sort_values('module_id', inplace=True)
cohort_module_count = enrolments.groupby('cohort_id')['MCode'].count().rename('module_count')
cohort_enrolments_total = enrolments.groupby('cohort_id')['Students3'].sum().rename('enrolments_total')

cohorts = cohorts.merge(cohort_module_count, on ='cohort_id')
cohorts = cohorts.merge(cohort_enrolments_total, on ='cohort_id')
cohorts.sort_values('cohort_id', inplace=True)

cohorts['mu_modules'] = cohorts.enrolments_total.astype('float')/cohorts.Students3

MODULES=list(cohorts['module_count'])
maxModules = max(MODULES)
enrolments.sort_values('module_id', inplace=True)

elective_topics = pd.read_csv(os.path.join("..", "curriculum_content", "coded", "stage2_coded_binary.csv"))

# only code the topics that are properly represented in the data set
code_set = list(set(elective_topics.columns) - set(['institution', 'elective']))
le_topics = preprocessing.LabelEncoder()
le_topics.fit(code_set)

# This is a bit naughty because two electives in different institutions 
# might have the same mcode
def mcode_has_topic(mcode, topic_id):
    [topic_code] = le_topics.inverse_transform([topic_id])
    if not topic_code in elective_topics.columns:
        return 0
    [result] = list( elective_topics[elective_topics['elective'] == mcode][topic_code])
    return result

def module_num_has_topic(cohort_num, module_num, topic_id):
    modules = enrolments[enrolments['cohort_id']==cohort_num].sort_values('module_id')
    mcode = modules.iloc[module_num]['MCode']
    return mcode_has_topic(mcode, topic_id)
    
def module_num_women(cohort_num, module_num):
    modules = enrolments[enrolments['cohort_id']==cohort_num].sort_values('module_id')
    women = int(modules.iloc[module_num]['Women3'])
    return women

def module_num_men(cohort_num, module_num):
    modules = enrolments[enrolments['cohort_id']==cohort_num].sort_values('module_id')
    men = int(modules.iloc[module_num]['Men3'])
    return men

cohort_module_women = np.zeros([len(cohorts), maxModules], dtype='int')
cohort_module_men = np.zeros([len(cohorts), maxModules], dtype='int')

cohort_module_topic_mapping = np.zeros([len(cohorts), maxModules, len(code_set)])

for cohort_id in range(len(cohorts)):
    cohort_modules = enrolments[enrolments['cohort_id']==cohort_id].sort_values('module_id')
    for module_num in range(len(cohort_modules.index)):
        cohort_module_women[cohort_id,module_num] = module_num_women(cohort_id, module_num)
        cohort_module_men[cohort_id,module_num] = module_num_men(cohort_id, module_num)
        for topic_id in range(len(code_set)):
#            print ("cohort", cohort_id, "module_num", module_num, "topic_id", topic_id)
            has_topic = module_num_has_topic(cohort_id, module_num, topic_id)
            cohort_module_topic_mapping[cohort_id,module_num,topic_id] = has_topic
            




print ("electives")
#print(electives)

model = CmdStanModel(stan_file=model_file + ".stan")

#print(code)

buildData={
    "COHORTS": len(cohorts.index),
    "cohort_women": list(cohorts['Women3']),
    "cohort_men": list(cohorts['Men3']),
    "mu_modules_taken": list(cohorts['mu_modules']),
    "TOPICS": len(code_set),
    "MAXMODULES": max(MODULES),
    "MODULES": MODULES,
    "module_topics": cohort_module_topic_mapping,
    "module_min_students": cohort_module_women,  # nonsense, but we don't use it
    "module_max_students": cohort_module_women,
    "module_women": cohort_module_women,
    "module_men": cohort_module_men
    }

fit = model.sample(data=buildData, chains=4, seed=seed, iter_sampling=num_samples)

fit_summary = az.summary(fit)
fit_cols = fit_summary.columns.to_flat_index()
#fit_cols[0] = "variable"
fit_summary.columns = fit_cols
fit_summary.to_csv('results/cmdstansummary-wg6-seed-' + str(seed) + '-samples-' + str(num_samples) + '-model-' + model_file + '.csv')

cohorts.to_csv("cohorts_with_ids.csv", index=False)
enrolments.to_csv("enrolments_with_ids.csv", index=False)
with open("topics.json", "w") as fp:
    json.dump(list(le_topics.inverse_transform(range(len(code_set)))), fp)
