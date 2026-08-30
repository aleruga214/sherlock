from enum import Enum

class EventType(Enum):
    LOG = "log"
    UNREACHABLE = "unreachable"
    NEVER_STARTED = "neverStarted"

# class to represent a log operation
class LogOperation:
    def __init__(self, typeLog, sessionId = None, dstService = None):
        self.dstService = str(dstService) if dstService is not None else None
        self.typeLog = str(typeLog) if typeLog is not None else None
        self.sessionId = int(sessionId) if sessionId is not None else None

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
    def __init__(self,serviceName,type,instance,timestamp,message, operation):
        self.serviceName = serviceName
        self.type = type            # log, unreacheable, never started
        self.instance = instance
        self.timestamp = timestamp
        self.message = message
        self.operation = operation  # object LogOperation


class Solution:
    def __init__(self, explanation, abductions):
        self.explanation = explanation
        self.abductions = abductions     

    # function for printing the possible failure cascades (only considering service names)
    def compactPrint(self,i):
        # print the explanation skeletons in "cascades"
        print(f"[{i}]: " + self.compactEventString(self.explanation[0]), end="\n  ")
        for event in self.explanation[1:]:
            print(" -> " + self.compactEventString(event), end="\n  ")
        print()
    
    # function for printing a single event in an explanation (without message)
    def compactEventString(self,e):
        eventString = e.serviceName + ": " 
        # return log template structure in case of logged events
        if e.type == EventType.LOG.value:
            eventString += e.operation.compact_str()
        elif e.type == EventType.NEVER_STARTED.value:
            eventString += "never started"
        elif e.type == EventType.UNREACHABLE.value:
            eventString += "unreachable"
        return eventString

    # function for printing all explanations (verbose, with message)
    def print(self,i):
        print(f"{i}: " + self.eventString(self.explanation[0]))
        for event in self.explanation[1:]:
            print(" -> " + self.eventString(event))
        print() 

        print("Abductions:")
        j=1
        for abduction in self.abductions:
            print(f"{j}) {self.eventString(abduction)}")
            j+=1
        print()    
        print("-"*50)

    # function for printing a single event in an explanation (verbose, with message)
    def eventString(self,e):
        if e.type == EventType.LOG.value:
            event = f"[{e.timestamp}] " if e.timestamp is not None else ""
            instance = e.instance if not str(e.instance).startswith("_") else ""
            event += instance + " (" + e.serviceName + "): " + str(e.operation)
            return event
        elif e.type == EventType.NEVER_STARTED.value:
            return e.serviceName + " never started"
        elif e.type == EventType.UNREACHABLE.value:
            return e.serviceName + " was unreachable"

    def __lt__(self, other):
        if len(self.abductions)==len(other.abductions): 
            return len(self.explanation)<len(other.explanation)
        return len(self.abductions)<len(other.abductions)

    @staticmethod
    def akinExplanation(exp1, exp2):
        if len(exp1) != len(exp2):
                return False
        i = 0       
        while i < len(exp1):
            if not(Solution.akinEvent(exp1[i],exp2[i])):
                return False
            i = i + 1
        return True

    @staticmethod
    def akinEvent(e1,e2):
            if e1.type == e2.type and e1.serviceName == e2.serviceName:
                if e1.type != EventType.LOG.value:
                    return True
                else:
                    msg1 = e1.operation.compact_str()
                    msg2 = e2.operation.compact_str()
                    if msg1 == msg2:
                        return True
                    else:
                        return False
            else:
                return False


def groupSolutions(solutions):
        # create an array "groupedSolutions" of solution groups
        # (solutions that have explanations with the same skeleton go in the same group)
        groupedSolutions = []
        for sol in solutions:
            if len(sol.explanation) > 0:
                expList = None
                if groupedSolutions != []:
                    for cascade in groupedSolutions:
                        if Solution.akinExplanation(sol.explanation,cascade[0].explanation):
                            expList = cascade
                            break
                if expList:
                    expList.append(sol)
                else:
                    expList = []
                    expList.append(sol)
                    groupedSolutions.append(expList)
        return groupedSolutions            


