# Generate synthetic data for module choices

import pandas as pd
import numpy as np
from numpy.random import default_rng

import stan
import arviz as az

from operator import itemgetter, attrgetter, methodcaller

from sklearn.utils import Bunch

import json
import argparse

parser = argparse.ArgumentParser(description='Generate synthetic data and use STAN model to extract parameters.')
parser.add_argument('--config', default='base_config.json', help='JSON config file defining cohorts module characteristics to generate synthetic data')
parser.add_argument('--samples', type=int, default=500)
parser.add_argument('--seed', type=int, default=1)
args = parser.parse_args()

configFilename = args.config
configFile = open(configFilename)
config = Bunch()
config.update(json.load(configFile))
configFile.close()

print("config", config)

seed = args.seed
num_samples = args.samples

print("seed ", seed, "num_samples", num_samples)

# base config defines these
"""
config.numCohorts = 8
config.numTopics = 20
config.maxTopics = 24
config.minModules = 10
config.maxModules = 20
config.minModuleChoices = 2
config.maxModuleChoices = 10
config.minStudents = 30
config.maxStudents = 500
config.minStudentsPerModule = 5
config.maxStudentsPerModule = 170
config.propWomen = 0.2
config.moduleMeanScore = 1000
config.sigmaModuleTopicScore = 200
config.sigmaWomenMenDiffRatio = 0.5
config.sigmaStudentRatio = 1
"""



sigmaWomenMenDiffTopicScore = config.sigmaModuleTopicScore * config.sigmaWomenMenDiffRatio
sigmaStudentScore = config.sigmaModuleTopicScore * config.sigmaStudentRatio

rng = default_rng(seed)


topicWeights = rng.exponential(config.maxTopics/config.numTopics, config.numTopics)
topicProbabilities = topicWeights/np.sum(topicWeights)
topicAllScores = rng.normal(0, config.sigmaModuleTopicScore, config.numTopics)
topicWomenMenDiffScores = rng.normal(0, sigmaWomenMenDiffTopicScore, config.numTopics)

print (config.numTopics, " topic probabilites ", topicProbabilities )

alpha_num = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

def moduleCode():
    length = 10
    return "MOD" + ''.join(rng.choice(alpha_num, size=length))

def studentCode():
    length = 12
    return "STU" + ''.join(rng.choice(alpha_num, size=length))

# TODO non-topic scores

allStudents = []
allModules = []
allCohorts = []

class Module:
    def __init__(self, cohort) -> None:
        self.code = moduleCode()
        self.cohort = cohort
        self.numTopics = rng.integers(low=config.minTopics, high=config.maxTopics+1)
        self.topics = rng.choice(config.numTopics, size=self.numTopics, p=topicProbabilities, replace=False)
        self.maxStudents = config.maxStudentsPerModule
        self.minStudents = config.minStudentsPerModule
        self.numWomen = 0
        self.numMen = 0
        self.students = []
        allModules.append(self)

    def __str__(self) -> str:
        return "code " + self.code + " topics " + str(self.topics) + " women " + str(self.numWomen) + "men " + str(self.numMen) + " wRatio " + str(self.propWomen())  +  " wScore " + str(self.womenScore()) + " aScore " + str(self.allScore())

    def addStudent(self, student) -> bool:
        if self.numStudents() >= config.maxStudents:
            return False
        self.students.append(student)
        if student.isWoman:
            self.numWomen += 1
        else:
            self.numMen += 1
        return True
    
    def removeStudent(self, student) -> bool:
        if not(student in self.students):
            print("Cannot remove student " + student.code)
            for s in self.students:
                print(s.code)
            return False
        self.students.remove(student)
        student.registeredModules.remove(m)
        if student.isWoman:
            self.numWomen -= 1
        else:
            self.numMen -= 1
        return True


    def numStudents(self):
        return self.numMen + self.numWomen

    def propWomen(self):
        if self.numStudents() > 0:
            return self.numWomen / self.numStudents()
        else:
            return 0

    def allScore(self):
        score = 0
        for topic in self.topics:
            score += topicAllScores[topic]
        return score

    def womenScore(self):
        score = self.allScore()
        for topic in self.topics:
            score += topicWomenMenDiffScores[topic]/2.0
        return score
    
    def menScore(self):
        score = self.allScore()
        for topic in self.topics:
            score -= topicWomenMenDiffScores[topic]/2.0
        return score
    
# topics as a binary list of length config.numTopics
    def topicLine(self):
        topicL = np.zeros(config.numTopics)
        for topic in self.topics:
            topicL[topic] = 1
        return topicL.tolist()


class Student:
    def __init__(self, cohort, isWoman) -> None:
        self.code = studentCode()
        self.cohort = cohort
        self.isWoman = isWoman
        self.numModules = 0
        self.preferredModules = []
        self.registeredModules = []
        cohort.students.append(self)
        allStudents.append(self)

    def __str__(self) -> str:
        return "student code " + self.code + "isWoman " + self.isWoman

    def allocateModules(self):
        while(len(self.registeredModules) < self.numModules and len(self.preferredModules)>0):
            (m,_) = self.preferredModules.pop()
            if(m.addStudent(self)):
                self.registeredModules.append(m)

class Cohort:
# numModules is the number of modules available for students to choose from
# muModules is the average number of modules selected by students
    def __init__(self, id, numModules, muModules) -> None:
        self.id = id
        self.modules = [None]*config.maxModules
        self.students = []
        self.numModules = numModules
        self.muModules = muModules
        allCohorts.append(self)

# filler to make uup from self.numModules to config.maxModules
    def filler(self, fill = 0):
        return [fill]*(config.maxModules - self.numModules)
    
# binary array of config.numTopics x config.maxModules
    def topicGrid(self):
        grid = list(map(methodcaller("topicLine"), self.modules[:self.numModules]))
        return grid + self.filler([0]*config.numTopics)
    
    def minStudents(self):
        return list(map(attrgetter("minStudents"), self.modules[:self.numModules])) + self.filler()
    
    def maxStudents(self):
        return list(map(attrgetter("maxStudents"), self.modules[:self.numModules])) + self.filler()
    
    def moduleWomen(self):
        return list(map(attrgetter("numWomen"), self.modules[:self.numModules])) + self.filler()

    def moduleMen(self):
        return list(map(attrgetter("numMen"), self.modules[:self.numModules])) + self.filler()
    
    def numWomen(self):
        return len([student for student in self.students if student.isWoman])
    
    def numMen(self):
        return len([student for student in self.students if not student.isWoman])
    
for cohortNum in range(config.numCohorts):
    numCohortModules = rng.integers(low=config.minModules, high=config.maxModules+1)
    muCohortModules = np.clip(rng.poisson((config.minModuleChoices + config.maxModuleChoices)/2), config.minModuleChoices, config.maxModuleChoices)
    cohort = Cohort(cohortNum, numCohortModules, muCohortModules)

    for moduleNum in range(numCohortModules):
        module = Module(cohort)
#        print("added module " + str(module) + " to " + str(cohort))
        cohort.modules[moduleNum] = module

    numStudents = rng.integers(low=config.minStudents, high=config.maxStudents + 1)

#    print ("cohort ", cohortNum, " numStudents ", numStudents, " numWomen ", numWomen)
    for studentNum in range(numStudents):
        isWoman = rng.binomial(1, config.propWomen)
        student = Student(cohort, isWoman)
        for moduleNum in range(numCohortModules):
            m = cohort.modules[moduleNum]
            muScore = config.moduleMeanScore
            if isWoman:
                muScore += m.womenScore()
            else:
                muScore += m.menScore()

# TODO add non-topic score
            studentModuleScore =rng.normal(muScore, sigmaStudentScore)
            student.preferredModules.append((m, studentModuleScore))
#            print ("student " + str(studentNum) + " has added preferred module " + str(m))
# favourite module at the end            
        student.preferredModules = sorted(student.preferredModules, key=itemgetter(1))
        student.numModules = np.clip(rng.poisson(muCohortModules), config.minModuleChoices, config.maxModuleChoices)
        student.allocateModules()

# remove modules with not enough students
for m in allModules:
#    print ("module ",m.code, " students " , m.numStudents())
    if m.numStudents() < config.minStudentsPerModule:
        print ("removing ", m.code, " which has " ,m.numStudents())

        for s in m.students:
#            print (s.code)
            if m.removeStudent(s):
                print(" removed student from", m.code)
            else:
                print(" failed to remove student from", m.code)
#            print("reallocating ", m.code)
            s.allocateModules()

#        print("after ", m.numStudents())
        

allModules = [module for module in allModules if module.numStudents()>0]

df = pd.DataFrame()
 
df['module'] = np.array(list(map(lambda m:m.code, allModules)))
df['numWomen'] = np.array(list(map(lambda m:m.numWomen, allModules)))
df['numMen'] = np.array(list(map(lambda m:m.numMen, allModules)))
df['wScore'] = np.array(list(map(lambda m:m.womenScore(), allModules)))
df['propWomen'] = np.array(list(map(lambda m:m.propWomen(), allModules)))

df.to_csv('results/synthetic-' + configFilename + '-seed-' + str(seed) + '.csv')

code_file=open("model.stan", "r")
code = code_file.read()

buildData={
    "COHORTS": config.numCohorts,
    "cohort_women": list(map(methodcaller("numWomen"),allCohorts)),
    "cohort_men": list(map(methodcaller("numMen"),allCohorts)),
    "mu_modules_taken": list(map(attrgetter("muModules"),allCohorts)),
    "TOPICS": config.numTopics,
    "MAXMODULES": config.maxModules,
    "MODULES": list(map(attrgetter("numModules"),allCohorts)),
    "module_topics": list(map(methodcaller("topicGrid"),allCohorts)),
    "module_min_students": list(map(methodcaller("minStudents"), allCohorts)),
    "module_max_students": list(map(methodcaller("maxStudents"), allCohorts)),
    "module_women": list(map(methodcaller("moduleWomen"), allCohorts)),
    "module_men": list(map(methodcaller("moduleMen"), allCohorts))
    }

# Fiddle on to make JSON encoding work

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return obj.__dict__
        if isinstance(obj, Cohort):
            return obj.id
        if isinstance(obj, Module):
            return obj.code
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

dumpData = {"buildData": buildData,
            "students": allStudents}

with open("results/build_data-" + configFilename + '-seed-' + str(seed) +  '.json', "w") as outfile:
    outfile.write(json.dumps(dumpData, indent=4, cls=NpEncoder))

posterior = stan.build(code, random_seed=seed, data=buildData)


fit = posterior.sample(num_chains=4, num_samples=num_samples)
fit_summary = az.summary(fit)
fit_cols = fit_summary.columns.to_flat_index()
fit_cols[0] = "variable"
fit_summary.columns = fit_cols
fit_summary.to_csv('results/stansummary-' + configFilename + '-seed-' + str(seed) + '-samples-' + str(num_samples) + '.csv')


results = []

for topic in range(config.numTopics):
    topic_text = "popularity_topic_all\[" + str(topic) + "\]"
    fit_topic_all = fit_summary[fit_summary['variable'].str.contains(topic_text)].iloc[0]['mean']
    topic_text = "popularity_topic_women_men_diff\[" + str(topic) + "\]"
    fit_topic_diff = fit_summary[fit_summary['variable'].str.contains(topic_text)].iloc[0]['mean']
    results.append({"topic": topic, "AllEst": fit_topic_all, "WomenMenEst": fit_topic_diff})

analysis_df = pd.DataFrame(results)
analysis_df['AllSynth'] = np.array(topicAllScores)
analysis_df['WomenMenSynth'] = np.array(topicWomenMenDiffScores)
analysis_df['Probability'] = np.array(topicProbabilities)
analysis_df.to_csv('results/topicssynthetic-' + configFilename + '-seed-' + str(seed) + '.csv')



            



