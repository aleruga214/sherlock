:- use_module(library(clpr)).

% Estrae l'intervallo temporale [Min, Max] da una variabile o costante numerica
extract_bounds(T, T, T) :-
    number(T).                      % Il timestamp è già un valore numerico fisso

extract_bounds(T, Min, Max) :-
    var(T),
    ( catch(inf(T, MinVal), _, fail) -> Min = MinVal ; Min = -inf ),
    ( catch(sup(T, MaxVal), _, fail) -> Max = MaxVal ; Max = inf ).

extract_bounds(T, -inf, inf) :- \+ var(T), \+ number(T).
    

% Arricchisce ogni evento con la coppia [Min, Max]
annotate_event(log(SI,I,T,E,M,Sev), bounded_event(log(SI,I,T,E,M,Sev), Min, Max)) :- %!,
    extract_bounds(T, Min, Max).
annotate_event(Event, Event) :- Event \= log(_,_,_,_,_,_).

% Predicato wrapper principale da chiamare da Python
solve_with_bounds(Goal, D_in, D_annotated, N_abducibles, N_remaining, Explanations, Root) :-
    distinct(solve(causedBy(Goal, Explanations_Raw, Root), D_in, D_Raw, N_abducibles, N_remaining, [], _)),
    maplist(annotate_event, Explanations_Raw, Explanations),
    maplist(annotate_event, D_Raw, D_annotated).