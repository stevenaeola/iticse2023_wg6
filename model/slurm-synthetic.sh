#!/bin/bash
# This line is required to inform the Linux
#command line to parse the script using
#the bash shell

# Instructing SLURM to locate and assign
#X number of nodes with Y number of
#cores in each node.
# X,Y are integers. Refer to table for
#various combinations
#SBATCH -N 1
#SBATCH -c 4
#SBATCH --mem=8g
#SBATCH -w cpu6

# Governs the run time limit and
# resource limit for the job. Please pick values
# from the partition and QOS tables below
#for various combinations
#SBATCH -p "cpu"
#SBATCH --qos="short"
#SBATCH -t 00-02:00:00

# Source the bash profile (required to use the module command)
source ~/WhatWomenStudy/analysis/stan/bin/activate

# Run your program (replace this with your program)
python3 synthetic.py --samples 16000

