#!/bin/bash

#elabora i file *brk.txt prodotti da acmant:
# estrae solo le righe dove compaiono le info sul numero di breakpoints e outliers per le stazioni
#elencate nel file "$1". "$1" in questo caso sono la lista delle stazioni trovate omogenee e 
#ancora in funzione nel 2015, suff. lunghe e complete (non per forza per 
#queste stazioni poi è possibile calcolare il climatologico, come ad esempio per l'Abruzzo).

#Il file $1 è l'intestazione del file seriea annuali omogenee trovate con climatol.

#1) crea un file fileGrep.txt con le stringhe regolari contenenti le stazioni elencate in $1
#2) il file fileGrep.txt viene utilizzatp per estrarre dai file *brk.txt le info 
#che contengono per le stazioni in $1 il numero di outliers e breakpoint

sed -e 's/^/ +[0-9]{1,} +[0-9]{1,} +/g' $1 | sed -e 's/$/ +/g' > fileGrep.txt
grep -E -f fileGrep.txt *brk.txt  | sed -e 's/ \+/;/g' > risultato.csv
