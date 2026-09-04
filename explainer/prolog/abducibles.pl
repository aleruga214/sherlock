abducible(log(SI,_,T,internal,_,err), D, D) :- once(log(SI,_,_,_,_,_)).

abducible(log(SI,_,T,received(_),_,info), D, D) :- once(log(SI,_,_,_,_,_)).

abducible(log(SI,_,T,sendTo(SJ,Id),_,info), D, D) :- 
    once(
        (log(SI,_,Te,okFrom(SJ,Id),_,info); 
        log(SI,_,Te,timeout(SJ,Id),_,err); 
        log(SI,_,Te,errorFrom(SJ,Id),_,err))
        ),
    dif(SI, SJ), 
    { T>=0, T=<Te }.

abducible(log(SI,_,T,sendTo(SJ,Id),_,info), D, D) :-
    once(
        (log(SI,_,_,sendTo(SJ,Id2),_,info), 
        log(SJ,_, Te,received(Id),_,info))
        ),
    dif(Id, Id2),
    dif(SI, SJ), 
    { T>=0 , T=<Te }.


abducible(log(SI,I,T,timeout(SJ,Id),_,err), D, D):- 
    once(
        (log(SI,_,Te,sendTo(SJ,Id),_,info);
        abducible(log(SI,_,Te,sendTo(SJ,Id),_,info),D, D))
        ),
    checkDoubleFailure(log(SI,I,_,timeout(SJ,Id),_,err), D),
    dif(SI, SJ).

abducible(log(SI,I,T,errorFrom(SJ,Id),_,err), D, D):- 
    once(
        (log(SI,_,_,sendTo(SJ,Id),_,info);
        abducible(log(SI,_,_,sendTo(SJ,Id),_,info),D, D))
        ),
    checkDoubleFailure(log(SI,I,_,errorFrom(SJ,Id),_,err), D),
    dif(SI, SJ).

/*
abducible(log(SI,I,T,timeout(SJ,Id),_,err), D, D) :- 
    once(
        (log(SI,_,_,sendTo(SJ,Id),_,info); 
        member(log(SI,_,_,sendTo(SJ,Id),_,info),D))
        ), !, %member(log(SI,_,_,sendTo(SJ,Id),_,info),D)
    checkDoubleFailure(log(SI,I,_,timeout(SJ,Id),_,err), D),
    dif(SI, SJ),
    {T>=0}.

abducible(log(SI,I,T,timeout(SJ,Id),_,err), D, [SendToLog | D]) :- 
    SendToLog = log(SI,I,Te,sendTo(SJ,Id),_,info),
    abducible(SendToLog, D, D),
    checkDoubleFailure(log(SI,I,_,timeout(SJ,Id),_,err), D),
    dif(SI, SJ),
    {T>=0, T>=Te}.

abducible(log(SI,I,T,errorFrom(SJ,Id),_,err), D, D) :- 
    once(
        (log(SI,_,_,sendTo(SJ,Id),_,info); 
        member(log(SI,_,_,sendTo(SJ,Id),_,info),D))
        ), !, %member(log(SI,_,_,sendTo(SJ,Id),_,info),D)
    checkDoubleFailure(log(SI,I,_,errorFrom(SJ,Id),_,err), D),
    dif(SI, SJ),
    {T>=0}.

abducible(log(SI,I,T,errorFrom(SJ,Id),_,err), D, [SendToLog | D]) :- 
    SendToLog = log(SI,I,Te,sendTo(SJ,Id),_,info),
    abducible(SendToLog, D, D),
    checkDoubleFailure(log(SI,I,_,errorFrom(SJ,Id),_,err), D),
    dif(SI, SJ),
    {T>=0, T>=Te}.
*/


checkDoubleFailure(log(SI,I,_,timeout(SJ,Id),_,err), D) :- 
    \+ member(log(SI,I,_,errorFrom(SJ,Id),_,err), D),
    \+ log(SI,I,_,errorFrom(SJ,Id),_,err),
    \+ log(SI,I,_,okFrom(SJ,Id),_,_).

checkDoubleFailure(log(SI,I,_,errorFrom(SJ,Id),_,err), D) :- 
    \+ member(log(SI,I,_,timeout(SJ,Id),_,err), D),
    \+ log(SI,I,_,timeout(SJ,Id),_,err),
    \+ log(SI,I,_,okFrom(SJ,Id),_,_).