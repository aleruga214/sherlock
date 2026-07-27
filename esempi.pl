
log(b, b1, 0, sendTo(a, 1), "prima richiesta", info).
%log(a, a1, 1, received(1), "richiesta ricevuta", info).
log(b, b1, 3, timeout(a, 1), "timeout primo errore", err).
 



%log(a, a1, 2, internal , "primo errore", err).