abducible(log(SI,_,_,internal,_,err), _) :- once(log(SI,_,_,_,_,_)).

abducible(log(SI,_,_,received(_),_,info), _) :- once(log(SI,_,_,_,_,_)).

abducible(log(SI,_,T,sendTo(SJ,Id),_,info), _) :- 
    once(
        (log(SI,_,Te,okFrom(SJ,Id),_,info); 
        log(SI,_,Te,timeout(SJ,Id),_,err); 
        log(SI,_,Te,errorFrom(SJ,Id),_,err))
        ),
    dif(SI, SJ), 
    { T=<Te }.

abducible(log(SI,_,T,sendTo(SJ,Id),_,info), _) :-
    once(
        (log(SI,_,_,sendTo(SJ,Id2),_,info), 
        log(SJ,_, Te,received(Id),_,info))
        ),
    dif(Id, Id2),
    dif(SI, SJ), 
    { T=<Te }.

abducible(log(SI,I,T,timeout(SJ,Id),_,err), D):- 
    SendToLog = log(SI,_,Ts,sendTo(SJ,Id),_,info),
    (SendToLog; 
    (\+ SendToLog, abducible(SendToLog,D)) ),
    checkDoubleFailure(log(SI,I,T,timeout(SJ,Id),_,err), D),
    dif(SI, SJ),
    { T >= Ts}.

abducible(log(SI,I,T,errorFrom(SJ,Id),_,err), D):- 
    SendToLog = log(SI,_,Ts,sendTo(SJ,Id),_,info),
    (SendToLog; 
    (\+ SendToLog, abducible(SendToLog,D)) ),
    checkDoubleFailure(log(SI,I,_,errorFrom(SJ,Id),_,err), D),
    dif(SI, SJ),
    { T >= Ts}.


checkDoubleFailure(log(SI,I,_,timeout(SJ,Id),_,err), D) :- 
    \+ member(log(SI,I,_,errorFrom(SJ,Id),_,err), D),
    \+ log(SI,I,_,errorFrom(SJ,Id),_,err),
    \+ log(SI,I,_,okFrom(SJ,Id),_,_).

checkDoubleFailure(log(SI,I,_,errorFrom(SJ,Id),_,err), D) :- 
    \+ member(log(SI,I,_,timeout(SJ,Id),_,err), D),
    \+ log(SI,I,_,timeout(SJ,Id),_,err),
    \+ log(SI,I,_,okFrom(SJ,Id),_,_).