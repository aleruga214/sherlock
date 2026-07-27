%abducible(log(_,_,_,Type,_,Sev)) :- check(Type, Sev).
abducible(log(_,_,_,internal,_,err)).
abducible(log(_,_,_,sendTo(_,_),_,_)).
abducible(log(_,_,_,received(_),_,_)).
check(Type, _) :- var(Type). %!.
%check(internal,Sev) :- !, Sev = err.
check(X,_) :- \+ var(X), dif(X,internal).
check(internal, err).


solve({C}, D, D, N, N) :- %!,
    call({C}).

solve(true,D,D, N, N). % :- !.


solve((A;B), D, NewD, N, NewN) :- %!,
    (solve(A, D, NewD, N, NewN) ; solve(B, D, NewD, N, NewN)).

solve(A, D, D, N, N) :-
    A \= (_,_), A \= (_;_),A \= {_},
    predicate_property(A, built_in), !,
    call(A).

solve((A,B),D,NewD, N, NewN) :- %!,
    solve(A,D,Dtemp, N, Ntemp), 
    solve(B,Dtemp,NewD, Ntemp, NewN).

solve(A,D,NewD, N, NewN) :- 
    A \= (_,_), A \= (_;_), A \= {_},
    clause(A,B), 
    solve(B,D,NewD, N, NewN).

solve(A,D,D, N, N) :- 
    A \= (_,_), A \= (_;_), A \= {_},
    \+ clause(A,_),
    member(A,D).

solve(A,D,[A|D], N, NewN) :- 
    N > 0,
    A \= (_,_), A \= (_;_), A \= {_},
    \+ clause(A,_), 
    \+ member(A,D),
    abducible(A), %!,
    NewN is N - 1.




