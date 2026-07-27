% meta-interprete vanilla abduttivo semplice
% solve(true,D,D):-!.
% solve((A,B),D,NewD) :- !, solve(A,D,Dtemp), solve(B,Dtemp,NewD).
% solve(A,D,NewD) :- clause(A,B), solve(B,D,NewD).
% solve(A,D,D) :- \+ clause(A,_),member(A,D).
% solve(A,D,[A|D]) :- \+ clause(A,_), \+ member(A,D).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% esempio 1
abducible(rainedLastNight).
abducible(sprinklerWasOn).
abducible(grassWet).
grassWet :- rainedLastNight.
grassWet :- sprinklerWasOn.
shoesWet :- grassWet.
% query :-trace,solve(shoesWet,[],X).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% esempio 2
abducible(born(_,_)).
abducible(resident(_,_)).
abducible(naturalised(_,_)).
abducible(mother(_,_)).
abducible(registered(_)).

citizen(X) :- born(X,usa).
citizen(X) :- resident(X,usa), naturalised(X,usa).
citizen(X) :- mother(Y,X), citizen(Y,usa), registered(X).
mother(mary,john).
citizen(mary,usa).
% query :-trace,solve(citizen(john),[],X).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
