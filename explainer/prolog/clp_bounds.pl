:- use_module(library(clpr)).

extractBounds(T, T, T) :-
    number(T).                      

extractBounds(T, Min, Max) :-
    var(T),
    ( catch(inf(T, MinVal), _, fail) -> Min = MinVal ; Min = -inf ),
    ( catch(sup(T, MaxVal), _, fail) -> Max = MaxVal ; Max = inf ).


annotateEvent(log(SI,I,T,E,M,Sev), boundedEvent(log(SI,I,T,E,M,Sev), Min, Max)) :- %!,
    extractBounds(T, Min, Max).
annotateEvent(Event, Event) :- Event \= log(_,_,_,_,_,_).


solveWithBounds(Goal, D, NewD, Ntot, N, NewExplanations, Root) :-
    distinct(solve(causedBy(Goal, Explanations, Root), D, Dtemp, Ntot, N, [], _)),
    maplist(annotateEvent, Explanations, NewExplanations),
    maplist(annotateEvent, Dtemp, NewD).