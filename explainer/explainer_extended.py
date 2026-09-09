from pyswip import Prolog
from explainer.model.solutions import Solutions

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

    goal = f"solveWithBounds({eventToExplain}, [], D, {nAbducibles}, N, Explanations,"
    goal += (rootCause) if rootCause is not None else "Root"
    goal += ")"

    if nSols is not None:
        query = f"limit({nSols}, {goal})."
    else:
        query = f"{goal}."    

    rootCauses = list(reasoner.query(query))
    return Solutions(rootCauses)