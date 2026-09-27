:- use_module(library(clpr)).

extractBounds(T,_,_, T, T) :-
    number(T).                      

extractBounds(T, Tmin, Tmax, Min, Max) :-
    var(T),
    ( catch(inf(T, MinVal), _, fail), number(MinVal), MinVal > -inf  
    -> Min = MinVal ; Min = Tmin ),
    ( catch(sup(T, MaxVal), _, fail), number(MaxVal), MaxVal < inf 
    -> Max = MaxVal ; Max = Tmax ).


annotateEvent(Tmin, Tmax,log(SI,I,T,E,M,Sev), boundedEvent(log(SI,I,T,E,M,Sev), Min, Max)) :- !,%
    extractBounds(T, Tmin, Tmax, Min, Max).
annotateEvent(_, _, Event, Event) :- Event \= log(_,_,_,_,_,_).


solveWithBounds(Goal, D, NewD, Ntot, N, NewExplanations, Root, Tmin, Tmax) :-
    checkGoal(Goal,D,Dtemp1),
    distinct(solve(causedBy(Goal, Explanations, Root), Dtemp1, Dtemp2, Ntot, N, [], _)),
    maplist(annotateEvent(Tmin, Tmax), Explanations, NewExplanations),
    maplist(annotateEvent(Tmin, Tmax), Dtemp2, NewD).

checkGoal(Goal, D, NewD):-
    (Goal ->  NewD = D;   NewD = [Goal|D]).