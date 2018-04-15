import time
import qmasm
import os
import sys
from subprocess import call


if __name__ == '__main__':

    methods = ['layout','dwave']
    #methods = ['dwave']
    #methods = ['layout']
    methods = ['dense']
    problems = ['maze3x3', 'maze6x6']
    #problems = ['maze3x3']
    trials = range(10)
    #trials = [1]


    results = {}

    for method in methods:
        results[method] = {}
        for problem in problems:
            results[method][problem] = {}
            for i in trials:
                results[method][problem][i] = {}
                log_file = 'log_%s_%s_%s.log' % (method,problem,i)

                cmd = "qmasm -vv -E --embed-method=%s --postproc=opt \
                --topology-file=../extras/chimera16.txt \
                --run %s.qmasm --locations-file=maze6x6.xy 2> %s" % (method,problem,log_file)
                os.system( cmd )

                file = open(log_file)
                table = False
                for line in file:
                    if 'Metric' in line:
                        table = True
                    if 'Maximum' in line:
                        max_chain_line = list(line.split())
                        max = max_chain_line[4]
                        results[method][problem][i]['max'] = max
                    if table:
                        if 'Physical' in line:
                            type, metric, value =  line.split()
                            results[method][problem][i][metric] = value


    for method in results:
        for problem in results[method]:
            for trial in results[method][problem]:
                for metric in results[method][problem][trial]:
                    print("%s %s %s %s %s" % (method, problem, trial, metric, results[method][problem][trial][metric]))
