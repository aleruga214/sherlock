# import Python default modules
import os,sys,getopt

from parser.templater.templater import Templater
from parser.parser import parseEvents
from explainer.explainer_extended import explain


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
    if len(args) < 4:
        cli_error("missing input arguments")
        exit(-1)

    eventLogLine = args[0]
    applicationLogs = args[1]
    templater = Templater(args[2])
    nAbducibles = args[3]

    # ******************
    # * PARSING INPUTS *
    # ******************
    # parse "event" to be explained and all events forming the "knowledgeBase"
    event = "event.pl"
    parseEvents(eventLogLine,event,templater)
    knowledgeBase = "knowledgeBase.pl"
    parseEvents(applicationLogs,knowledgeBase,templater)
    
    # ***********************
    # * ROOT CAUSE ANALYSIS *
    # ***********************
    solutions = explain(event,knowledgeBase, nAbducibles, nSols, rootCause)

    # *****************
    # * PRINT RESULTS *
    # *****************
    solutions.sort()

    if verbose:
        solutions.print()
    else:
        solutions.compactPrint(templater)

    solutions.marshal(templater,"explanations.txt")

    if solutions.size()==0:
        rc = (" from " + rootCause) if rootCause!=None else "" 
        print("Found no failure cascade" + rc + " to the considered event")
    else:
        end = "s" if solutions.size() > 1 else "" # plural or singular
        print("Found a total of " + str(solutions.size()) + " possible explanation" + end)

    # Remove generated files
    os.remove(event) # comment this, if needing to keep files for Prolog debugging
    os.remove(knowledgeBase) # comment this, if needing to keep files for Prolog debugging

# function for printing cli erros, followed by cli usage
def cli_error(message):
    print("ERROR: " + message + ".")
    print()
    cli_help()

# function for printing cli usage
def cli_help():
    print("Usage of sherlock.py is as follows:")
    print("  sherlock.py [OPTIONS] EVENT LOGS TEMPLATES ABDUCIBLES")
    print("where EVENT and LOGS are JSON files, TEMPLATES is a YAML file, ABDUCIBLES is an integer number, and OPTIONS can be")
    print("  [--help] to print a help on the usage of sherlock.py")
    print("  [-n N|--num=N] to set to N the amount of possible explanations to identify")
    print("  [-r X|--root=X] to require X to be the root cause of identified explanations")
    print("  [-v|--verbose] to print verbose analysis results")
    print()    

if __name__ == "__main__":
    main(sys.argv[1:])