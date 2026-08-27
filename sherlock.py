# import Python default modules
import os,sys,getopt

from pyswip import Prolog
from pyswip import Variable
from solutions import *
from datetime import datetime


def explain(event,applicationLogs, nAbducibles, nSols, rootCause):
    # create Prolog reasoner
    reasoner = Prolog()
    
    # load knowledge base
    reasoner.consult("explainer/prolog/severity.pl")
    reasoner.consult("explainer/prolog/explain.pl")
    reasoner.consult("explainer/prolog/meta_interpreter.pl")
    reasoner.consult("explainer/prolog/abducibles.pl")
    reasoner.consult(applicationLogs)
    
    # read event to explain
    eventFile = open(event,"r")
    eventToExplain = eventFile.readline() # read line corresponding to event
    eventFile.close()
    eventToExplain = eventToExplain[:len(eventToExplain)-2] # remove "." and "\n" at the end

    # run Prolog reasoner to find (and return) root causes
    query = f"distinct(solve(causedBy({eventToExplain}, Explanations, "
    query += (rootCause) if rootCause is not None else "Root" # use "Root" if rootCause is not specified
    query += f"),[], D, {nAbducibles}, N, [], _))."

    rootCauses = list(reasoner.query(query))
    return explanations(rootCauses)

def explanations(solutionsList):
    solutions = []
    
    for solution in solutionsList:
        sol = Solutions([],[])
        ppExp = [] # post-processed explanation
        ppAbd = []
         
        explanation = solution["Explanations"]
        abduction = solution["D"]

        for event in explanation:
            # post-processed event info
            serviceName = str(event.args[0])
            type = None
            instance = None
            timestamp = None
            message = None 

            eventType = str(event.name)
            # case: event = "log(serviceName,instanceId,timestamp,_,_)"
            if eventType == EventType.LOG.value:
                type = str(event.args[3])
                instance = str(event.args[1])
                t_val = event.args[2]
                if not isinstance(t_val, Variable):
                    timestamp = datetime.fromtimestamp(event.args[2]) # timestamp saved as ISO
                message = str(event.args[4])
            elif not(eventType == EventType.UNREACHABLE.value or eventType == EventType.NEVER_STARTED.value) :
                raise TypeError("unknown event type " + eventType) # to avoid missing events (if not corresponding to a known type)
            ppExp.append(Event(serviceName,type,instance,timestamp,message,eventType))
        
        sol.explanation = ppExp

        for event in abduction:
            # post-processed event info
            serviceName = str(event.args[0])
            type = None
            instance = None
            timestamp = None
            message = None 
            eventType = str(event.name)
            # event = "log(serviceName,instanceId,timestamp,_,_)"
            type = str(event.args[3])
            instance = str(event.args[1])
            t_val = event.args[2]
            if not isinstance(t_val, Variable):
                timestamp = datetime.fromtimestamp(event.args[2]) # timestamp saved as ISO
            message = str(event.args[4])
            ppAbd.append(Event(serviceName,type,instance,timestamp,message, eventType))
        sol.abductions = ppAbd
        solutions.append(sol)    
    return solutions
    

def main(argv):

    # parse command line arguments
    try:
        options,args = getopt.getopt(argv,"hn:r:v",["help","num=","root=","verbose"])
    except: 
        cli_error("wrong options used")
        exit(-1)

    # options to customise the execution of the explainer (with default values)
    nSols = None # number of possible explanations to find (default: all)
    rootCause = None # value for root cause (default: all)
    verbose = False # by default, only "compact" printing (service names, no instances/timestamps/messages)

    # getting specified options
    for option, value in options:
        # help 
        if option in ["-h","--help"]:
            cli_help()
            exit(0)
        # setting number of solutions to identify
        elif option in ["-n","--num"]:
            if value.isnumeric() and float(value)>0:
                nSols = value
            else: 
                cli_error("the amount of solutions to find must be a positive number")
                exit(-2)
        # setting root causing service
        elif option in ["-r","--rootCause"]:
            rootCause = value
        # setting verbosity
        elif option in ["-v","--verbose"]:
            verbose = True

    # check & process command line arguments
    if len(args) < 3:
        cli_error("missing input arguments")
        exit(-1)

    event = args[0]
    knowledgeBase = args[1]
    nAbducibles = args[2]
    
    # ***********************
    # * ROOT CAUSE ANALYSIS *
    # ***********************
    solutions = explain(event,knowledgeBase, nAbducibles, nSols, rootCause)

    # *****************
    # * PRINT RESULTS *
    # *****************
    solutions.sort()
    i = 0
    for s in solutions:
    #        s.print()
        i+=1
        if verbose:
            s.print(i)
        else:
            s.compactPrint(i)
    #solutions.marshal(templater,"explanations.txt")

    if len(solutions)==0:
        rc = (" from " + rootCause) if rootCause!=None else "" 
        print("Found no failure cascade" + rc + " to the considered event")
    else:
        end = "s" if len(solutions) > 1 else "" # plural or singular
        print("Found a total of " + str(len(solutions)) + " possible explanation" + end)
    

# function for printing cli erros, followed by cli usage
def cli_error(message):
    print("ERROR: " + message + ".")
    print()
    cli_help()

# function for printing cli usage
def cli_help():
    print("Usage of sherlock.py is as follows:")
    print("  sherlock.py [OPTIONS] EVENT LOGS ABDUCIBLES")
    print("where EVENT and LOGS are JSON files, ABDUCIBLES is an integer number, and OPTIONS can be")
    print("  [--help] to print a help on the usage of yrca.py")
    print("  [-n N|--num=N] to set to N the amount of possible explanations to identify")
    print("  [-r X|--root=X] to require X to be the root cause of identified explanations")
    print("  [-v|--verbose] to print verbose analysis results")
    print()    

if __name__ == "__main__":
    main(sys.argv[1:])