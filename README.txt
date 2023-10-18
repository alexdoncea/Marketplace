Doncea Ilie-Alexandru 341C4 - Tema 1 ASC

Tema necesita implementarea problemei Multiple-Producers-Multiple-Consumers.
Producatorii adauga la infinit produse in marketplace, iar consumatorii parcurg
lista de produse si adauga in cos ce doresc. Marketplace-ul va face operatiile
de a publica un produs, de a crea un cos nou, de a scoate si a adauga produse
din cos, si in final de a plasa comanda unui consumer.
Pentru a nu exisa probleme cu paralelizarea threadurilor am folosit elemente
thread-safe, iar unde a fost nevoie am folosit si lock-uri pentru a evita
aparitia race condition-urilor (spre exemplu in lucrul cu id-urile cosurilor
sau produselor).
Tema a fost complet implementata, avand atat elementele de marketplace cat si
clasa de unitteste, care are aceleasi teste cu cele oferite in folderul tests,
cat si logging-ul in aplicatie.

Resurse:
    - laboaratoarele 1-3 de ASC
    - Stack Overflow pentru cateva erori (spre exemplu checkerul de code style
    imi sugera sa folosesc "with" cand foloseam lock-uri si am cautat cum se
    folosesc)