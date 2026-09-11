from enum import Enum
from datetime import datetime
from pyswip import Variable
from pyswip import Atom
from pyswip import Functor

class EventType(Enum):
    LOG = "log"
    UNREACHABLE = "unreachable"
    NEVER_STARTED = "neverStarted"                                               

# class to represent a log operation
class LogOperation:
    def __init__(self, typeLog, sessionId = None, dstService = None):
        self.dstService = str(dstService) if dstService is not None else None
        self.typeLog = str(typeLog) if typeLog is not None else None
        self.sessionId = str(sessionId) if sessionId is not None else None

    @classmethod
    def atom(cls, op):
        return cls(op)

    @classmethod
    def functor(cls, op):
        if(len(op.args))==2:
            return cls(op.name, op.args[1], op.args[0]) 
        else:
            return cls(op.name, op.args[0])

    def __str__(self):
        if(self.sessionId == None):
            return self.typeLog
        elif(self.dstService == None):
            return f"{self.typeLog}({self.sessionId})"
        else:
            return f"{self.typeLog}({self.dstService},{self.sessionId})"

    def compact_str(self):
        if self.dstService:
            return f"{self.typeLog}({self.dstService})"
        return str(self.typeLog)

    
# class to represent an event
class Event:
    def __init__(self,serviceName,type,instance,timestamp,message, operation, t_min, t_max):
        self.serviceName = serviceName
        self.type = type            # log, unreacheable, never started
        self.instance = instance
        self.timestamp = timestamp
        self.message = message
        self.operation = operation  # object LogOperation
        self.t_min = t_min
        self.t_max = t_max 

    # function for printing a single event in an explanation (verbose, with message)
    def __str__(self):
        if self.type == EventType.LOG.value:
            event = f"[{self.timestamp}] " if self.timestamp is not None else f"[T ∈ [{self.t_min}, {self.t_max}]] "
            instance = self.instance if not str(self.instance).startswith("_") else ""
            event += instance + " (" + self.serviceName + "): " + str(self.operation)
            return event
        elif self.type == EventType.NEVER_STARTED.value:
            return self.serviceName + " never started"
        elif self.type == EventType.UNREACHABLE.value:
            return self.serviceName + " was unreachable" 

    # function for printing a single event in an explanation (without message)
    def compactEventString(self):
        eventString = self.serviceName + ": " 
        # return log template structure in case of logged events
        if self.type == EventType.LOG.value:
            eventString += self.operation.compact_str()
        elif self.type == EventType.NEVER_STARTED.value:
            eventString += "never started"
        elif self.type == EventType.UNREACHABLE.value:
            eventString += "unreachable"
        return eventString        


class Solution:
    def __init__(self, explanation, abductions):
        self.explanation = explanation
        self.abductions = abductions     

    # function for printing the possible failure cascades (only considering service names)
    def compactPrintSolution(self,i):
        # print the explanation skeletons in "cascades"
        print(f"[{i}]: " + self.explanation[0].compactEventString())
        for event in self.explanation[1:]:
            print(" -> " + event.compactEventString())
        print()

    # function for printing all explanations (verbose, with message)
    def printSolution(self,i):
        print(f"{i}: {self.explanation[0]}")
        for event in self.explanation[1:]:
            print(f" -> {event}")
        print() 

        line = "Abductions:" if (len(self.abductions)!=0) else "No Abductions needed!"
        
        print(line) 
        for j,abduction in enumerate(self.abductions, start=1):
            print(f"{j}) {abduction}")
        print()
           
        print("-"*50)

    def __lt__(self, other):
        if len(self.abductions)==len(other.abductions): 
            return len(self.explanation)<len(other.explanation)
        return len(self.abductions)<len(other.abductions)

    @staticmethod
    def akinExplanation(exp1, exp2, templater):
        if len(exp1) != len(exp2):
                return False
        i = 0       
        while i < len(exp1):
            if not(Solution.akinEvent(exp1[i],exp2[i], templater)):
                return False
            i = i + 1
        return True

    @staticmethod
    def akinEvent(e1,e2, templater):
            if e1.type == e2.type and e1.serviceName == e2.serviceName:
                if e1.type != EventType.LOG.value:
                    return True
                else:
                    msg1 = templater.parseMessage(e1.message)
                    msg2 = templater.parseMessage(e2.message)               
                    # msg1 = e1.operation.compact_str()
                    # msg2 = e2.operation.compact_str()
                    if msg1 == msg2:
                        return True
                    else:
                        return False
            else:
                return False

class Solutions:
    def __init__(self, solutionsList):
        self.solutions = []
            
        for solution in solutionsList:
            sol = Solution([],[])
            ppExp = [] # post-processed explanation
            ppAbd = []
                
            explanation = solution["Explanations"]
            abductions = solution["D"]
    
            ppExp = self.processEvents(explanation)
            sol.explanation = ppExp
    
            ppAbd = self.processEvents(abductions)
            sol.abductions = ppAbd
    
            self.solutions.append(sol)     

    
    def processEvents(self, events_list):
        ppList = []
        for item in events_list:
            if str(item.name) == "boundedEvent":
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

    def groupSolutions(self, templater):
            # create an array "groupedSolutions" of solution groups
            # (solutions that have explanations with the same skeleton go in the same group)
            if self.size() == 0:
                return
            
            groupedSolutions = []
            for sol in self.solutions:
                if len(sol.explanation) > 0:
                    expList = None
                    if groupedSolutions != []:
                        for cascade in groupedSolutions:
                            if Solution.akinExplanation(sol.explanation,cascade[0].explanation, templater):
                                expList = cascade
                                break
                    if expList:
                        expList.append(sol)
                    else:
                        expList = []
                        expList.append(sol)
                        groupedSolutions.append(expList)
            return groupedSolutions            

    # function for marshalling all explanations (verbose, with message)
    def marshal(self,templater,outputFile):
        solLists = self.groupSolutions(templater)
        output = open(outputFile,"w")
        output.write("* "*40 + "\n")
        for solList in solLists:
            for sol in solList:
                output.write(f"\n {sol.explanation[0]} \n")
                for event in sol.explanation[1:]:
                    output.write(f" -> {event} \n")
            output.write("\n" + "* "*40 + "\n")
        output.close()

    def sort(self):
        self.solutions.sort()

    def size(self):
        return len(self.solutions)  
  

    def compactPrint(self, templater):
        groupedSolutions = self.groupSolutions(templater)
        # print the explanation skeletons in "cascades"
        for s in groupedSolutions:
            percentage = round(len(s)/self.size(),3)
            s[0].compactPrintSolution(percentage)

    def print(self):
        for i,s in enumerate(self.solutions, start=1):
            s.printSolution(i)
