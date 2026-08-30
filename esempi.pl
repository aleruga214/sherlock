
log(b, b1, 0, sendTo(a, 1), "prima richiesta", info).
log(b, b2, 0, sendTo(a,5), "seconda richiesta", info).
log(b, b2, 3, timeout(a, 5), "timeout primo errore", err).
log(c,c2, 4, timeout(b,6), "timeout", err).
%log(a, a1, 1, received(1), "richiesta ricevuta", info).
log(b, b1, 3, timeout(a, 1), "timeout primo errore", err).
log(c,c1, 4, timeout(b,2), "timeout secondo errore", err).
log(d, d1, 5, timeout(c, 3), "timeout terzo errore", err).
%log(a, a1, 6, received(4), "richiesta ricevuta", info).
 



%log(a, a1, 2, internal , "primo errore", err).