solve({C}, D, D, N, N, H, H) :- %!,
    call({C}).

solve(true, D, D, N, N, H, H):- !. 

solve(\+A, D, D, N, N, H, H) :-
    \+solve(A, D, _, 0, _, H, _).

solve((A;B), D, NewD, N, NewN, H, NewH) :- %!,
    (solve(A, D, NewD, N, NewN, H, NewH) ; solve(B, D, NewD, N, NewN, H, NewH)).

solve(A, D, D, N, N, H, H) :-
    A \= (_,_), A \= (_;_),A \= {_}, A \= (\+_),     
    predicate_property(A, built_in), !,
    call(A).

solve((A,B), D, NewD, N, NewN, H, NewH) :- %!,
    solve(A,D,Dtemp, N, Ntemp, H, Htemp), 
    solve(B,Dtemp,NewD, Ntemp, NewN, Htemp, NewH).

solve(A, D,NewD, N, NewN, H, NewH) :- 
    A \= (_,_), A \= (_;_), A \= {_}, A \= (\+_),
    checkHistory(A, H, Htemp),
    clause(A,B), 
    solve(B, D,NewD, N, NewN, Htemp, NewH).

solve(A,D,D, N, N, H, H) :- 
    A \= (_,_), A \= (_;_), A \= {_}, A \= (\+_),
    \+ clause(A,_),
    member(A,D).

solve(A,D,[A|Dtemp], N, NewN, H, H) :- 
    N > 0,
    A \= (_,_), A \= (_;_), A \= {_}, A \= (\+_),
    \+ clause(A,_), 
    \+ member(A,D),
    abducible(A, D, Dtemp),%!, 
    NewN is N - 1.


checkHistory(A,H,[A|H]):- 
    A = causedBy(_,_,_), 
    \+ member(A,H).

checkHistory(A, H, H) :- 
    A \= causedBy(_,_,_).


