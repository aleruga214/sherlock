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
    def __init__(self,serviceName,type,instance,timestamp,message, operation, t_min, t_max, severity):
        self.serviceName = serviceName
        self.type = type            # log, unreacheable, never started
        self.instance = instance
        self.timestamp = timestamp
        self.message = message
        self.operation = operation  # object LogOperation
        self.t_min = t_min
        self.t_max = t_max 
        self.severity = severity

    # function for printing a single event in an explanation (verbose, with message)
    def __str__(self):
        if self.type == EventType.LOG.value:
            timestamp = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if self.timestamp else None
            if not isinstance(self.t_min, str):
                t_min = datetime.fromtimestamp(self.t_min).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]            
            else:
                t_min = self.t_min 
            if not isinstance(self.t_max, str):
                t_max = datetime.fromtimestamp(self.t_max).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
            else:
                t_max = self.t_max    
            event = f"[{timestamp}] " if timestamp is not None else f"[T ∈ [{t_min}, {t_max}]] "
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
    def compactPrintSolution(self,perc, min_abd):
        # print the explanation skeletons in "cascades"
        print(f"[min abductions: {min_abd}][{perc*100:.1f}%]: {self.explanation[0].compactEventString()}")
        for event in self.explanation[1:]:
            print(" -> " + event.compactEventString())
        print()

    # function for printing all explanations (verbose, with message)
    def printSolution(self,i, perc):
        print("-"*50)
        print(f"Solution {i} [{perc*100:.1f}%]")
        print("-"*50)
        print(f"▶ {self.explanation[0]}")
        for event in self.explanation[1:]:
            print(f" -> {event}")
        print() 

        line = "Abductions:" if (len(self.abductions)!=0) else "No Abductions needed!"
        
        print(line) 
        for j,abduction in enumerate(self.abductions, start=1):
            print(f"{j}) {abduction}")
        print()
           

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
                    return (e1.operation.typeLog == e2.operation.typeLog 
                            and e1.operation.dstService==e2.operation.dstService)  
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

                t_min = float(item.args[1])
                
                t_max = float(item.args[2])

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
            severity = None
            # case: event = "log(serviceName,instanceId,timestamp,_,_)"
            if type == EventType.LOG.value:
                if isinstance(event.args[3],Atom):
                    operation = LogOperation.atom(event.args[3])
                else:
                    operation = LogOperation.functor(event.args[3])    
                instance = str(event.args[1])
                t_val = event.args[2]
                if not isinstance(t_val, Variable):
                    timestamp = float(t_val)
                message = str(event.args[4])
                severity = str(event.args[5])
            elif not(type == EventType.UNREACHABLE.value or type == EventType.NEVER_STARTED.value) :
                raise TypeError("unknown event type " + type) # to avoid missing events (if not corresponding to a known type)
            ppList.append(Event(serviceName,type,instance,timestamp,message,operation, t_min, t_max, severity))
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

        groups = []

        for group in groupedSolutions:
            minAbductions = min(len(s.abductions) for s in group)
            frequency = len(group)
            chainLength = len(group[0].explanation)

            groups.append((group, minAbductions, frequency, chainLength))

        sortedGroups = sorted(groups, key=lambda g: (g[1], -g[2], g[3]))

        for group, minAbductions, frequency, chainLength in sortedGroups:
            percentage = round(frequency / self.size(), 3)
            group[0].compactPrintSolution(percentage, minAbductions)


    def print(self, templater):
        groupedSolutions = self.groupSolutions(templater)
        frequencies = {}

        for group in groupedSolutions:
            frequency = len(group)

            for solution in group:
                frequencies[id(solution)] = frequency

        def individualSortKey(sol):
            frequency = frequencies.get(id(sol), 1)
            return (len(sol.abductions), -frequency, len(sol.explanation))
            
        sortedSolutions = sorted(self.solutions, key=individualSortKey)

        for i,s in enumerate(sortedSolutions, start=1):
            percentage = round(frequencies[id(s)] / self.size(), 3)
            s.printSolution(i,percentage)
