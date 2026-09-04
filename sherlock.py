# import Python default modules
import os,sys,getopt

from pyswip import Prolog
from pyswip import Variable
from pyswip import Atom
from pyswip import Functor
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
    reasoner.consult("explainer/prolog/clp_bounds.pl")
    reasoner.consult(applicationLogs)
    
    # read event to explain
    eventFile = open(event,"r")
    eventToExplain = eventFile.readline() # read line corresponding to event
    eventFile.close()
    eventToExplain = eventToExplain[:len(eventToExplain)-2] # remove "." and "\n" at the end

    goal = f"solve_with_bounds({eventToExplain}, [], D, {nAbducibles}, N, Explanations,"
    goal += (rootCause) if rootCause is not None else "Root"
    goal += ")"
    # run Prolog reasoner to find (and return) root causes
    # goal = f"distinct(solve(causedBy({eventToExplain}, Explanations, "
    # goal += (rootCause) if rootCause is not None else "Root" # use "Root" if rootCause is not specified
    # goal += f"),[], D, {nAbducibles}, N, [], _))"

    if nSols is not None:
        query = f"limit({nSols}, {goal})."
    else:
        query = f"{goal}."    

    rootCauses = list(reasoner.query(query))
    return parseSolutions(rootCauses)


def parseSolutions(solutionsList):
    solutions = []
    
    for solution in solutionsList:
        sol = Solution([],[])
        ppExp = [] # post-processed explanation
        ppAbd = []
         
        explanation = solution["Explanations"]
        abductions = solution["D"]

        ppExp = parseEvents(explanation)
        sol.explanation = ppExp

        ppAbd = parseEvents(abductions)
        sol.abductions = ppAbd

        solutions.append(sol)    
    return solutions


def parseEvents(list):
    ppList = []
    for item in list:
        if str(item.name) == "bounded_event":
            event = item.args[0]
            t_min = datetime.fromtimestamp(item.args[1]) if not isinstance(item.args[1],Atom) and not isinstance(item.args[1],Functor) else item.args[1]
            t_max = datetime.fromtimestamp(item.args[2]) if not isinstance(item.args[2],Atom) and not isinstance(item.args[2],Functor)else item.args[2]

        else:
            event = item 
            t_max = None
            t_min = None

        # post-processed event info
        serviceName = str(event.args[0])
        operation = None
        instance = None
        timestamp = None
        message = None 
        type = str(event.name)
        # case: event = "log(serviceName,instanceId,timestamp,_,_)"
        if type == EventType.LOG.value:
            if isinstance(event.args[3],Atom):
                operation = LogOperation.atom(event.args[3])
            else:
                operation = LogOperation.functor(event.args[3])    
            instance = str(event.args[1])
            t_val = event.args[2]
            if not isinstance(t_val, Variable):
                timestamp = datetime.fromtimestamp(t_val) # timestamp saved as ISO
            message = str(event.args[4])
        elif not(type == EventType.UNREACHABLE.value or type == EventType.NEVER_STARTED.value) :
            raise TypeError("unknown event type " + type) # to avoid missing events (if not corresponding to a known type)
        ppList.append(Event(serviceName,type,instance,timestamp,message,operation, t_min, t_max))
    return ppList 


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
    print("  [--help] to print a help on the usage of sherlock.py")
    print("  [-n N|--num=N] to set to N the amount of possible explanations to identify")
    print("  [-r X|--root=X] to require X to be the root cause of identified explanations")
    print("  [-v|--verbose] to print verbose analysis results")
    print() 


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
        elif option in ["-r","--root"]:
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

    if verbose:
        for i,s in enumerate(solutions, start=1):
            s.print(i)
    else:
        groupedSolutions = groupSolutions(solutions)
        for s in groupedSolutions:
            percentage = round(len(s)/len(solutions),3)
            s[0].compactPrint(percentage)

    if len(solutions)==0:
        rc = (" from " + rootCause) if rootCause!=None else "" 
        print("Found no failure cascade" + rc + " to the considered event")
    else:
        end = "s" if len(solutions) > 1 else "" # plural or singular
        print("Found a total of " + str(len(solutions)) + " possible explanation" + end)
   

if __name__ == "__main__":
    main(sys.argv[1:])