from enum import Enum

class EventType(Enum):
    LOG = "log"
    UNREACHABLE = "unreachable"
    NEVER_STARTED = "neverStarted"

# class to represent an event
class Event:
    def __init__(self,serviceName,type,instance,timestamp,message, eventType):
        self.serviceName = serviceName
        self.type = type
        self.instance = instance
        self.timestamp = timestamp
        self.message = message
        self.eventType = eventType


class Solutions:
    def __init__(self, explanation, abductions):
        self.explanation = explanation
        self.abductions = abductions 

    # def print(self, indent="   "):
       
    #     # 1. Stampa della Catena Causale
    #     print("\nExplanation:")
    #     if not self.explanation:
    #         print(f"{indent}(Nessun evento nella catena)")
    #     else:
    #         cont = 1
    #         for event in self.explanation:
    #             ts_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S") if event.timestamp else "N/A"
    #             inst_str = f" [Istanza: {event.instance}]" if event.instance else ""
    #             msg_str = f' - "{event.message}"' if event.message else ""
                
    #             print(f"{cont})  [{event.eventType}] Servizio: {event.serviceName}{inst_str}")
    #             print(f"{indent}   Tipo: {event.type}")
    #             print(f"{indent}   Timestamp: {ts_str}{msg_str}")
    #             cont+=1

    #     # 2. Stampa dei Fatti Abdotti 
    #     print("\nAbduzioni generate:")
    #     if not self.abductions:
    #         print(f"{indent}(Nessuna abduzione generata)")
    #     else:
    #         for event in self.abductions:
    #             ts_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S") if event.timestamp else "N/A"
    #             inst_str = f" [Istanza: {event.instance}]" if event.instance else ""
    #             msg_str = f' - "{event.message}"' if event.message else ""
                
    #             print(f"- [{event.eventType}] Servizio: {event.serviceName}{inst_str}")
    #             print(f"{indent}  Tipo: {event.type}")
    #             print(f"{indent}  Timestamp: {ts_str}{msg_str}")

    #     print("=" * 60 + "\n")    

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
        if e.eventType == EventType.LOG.value:
            eventString += e.type
        elif e.eventType == EventType.NEVER_STARTED.value:
            eventString += "never started"
        elif e.eventType == EventType.UNREACHABLE.value:
            eventString += "unreachable"
        return eventString

    # function for printing all explanations (verbose, with message)
    def print(self,i):
        print(f"[{i}]: " + self.eventString(self.explanation[0]))
        for event in self.explanation[1:]:
            print(" -> " + self.eventString(event))
        print() 

        print("Abduzioni:")
        j=1
        for abduction in self.abductions:
            print(f"{j}) {self.eventString(abduction)}")
            j+=1
        print()

     # function for printing a single event in an explanation (verbose, with message)
    def eventString(self,e):
        if e.eventType == EventType.LOG.value:
            timestamp = str(e.timestamp)
            return "[" + timestamp + "] " + e.instance + " (" + e.serviceName + "): " + e.message
        elif e.eventType == EventType.NEVER_STARTED.value:
            return e.serviceName + " never started"
        elif e.eventType == EventType.UNREACHABLE.value:
            return e.serviceName + " was unreachable"

    def __lt__(self, other):
        # if len(self.abductions)==len(other.abduction): 
        #     return 
        return len(self.abductions)<len(other.abductions)
                      
