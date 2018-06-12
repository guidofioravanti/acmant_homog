#elabora i risultati dell'omogeneizzazione dei dati giornalieri. 
#ACMANT produce per i dati giornalieri i seguenti file:
# un file di dati giornalieri omogeneizzati (v.txt)
#i file j.txt e t.txt analoghi a quelli prodotti per l'omogeneizzazione dei mensili (ovvero si tratta delle medie mensili e dei flag
#associati a tali medie)

#Vogliamo elaborare i dati giornalieri ma abbiamo bisogno di scartare eventuali dati prodotti da ACMANT come effetto di interpolazione
#(in realtà non è chiaro se per i dati giornalieri ACMANT produca un riempimento dei buchi). Per evitare dubbi leggiamo i dati
#giornalieri omogeneizzati e le serie originali, sostituiamo NA laddove il dato originario contiene NA.
import glob
import sys
import numpy as np
import pandas as pd
import re
import pdb
from functools import reduce
import os

annoI=1961
annoF=2015
calendario=pd.date_range(start="{}-01-01".format(annoI),freq="D",end="{}-12-31".format(annoF))
calendario=pd.DataFrame({"yymmdd":calendario})
calendario.yymmdd=calendario.yymmdd.astype(str)
calendario=calendario.yymmdd.str.split("-",expand=True)
calendario.columns=["yy","mm","dd"]
calendario.yy=calendario.yy.astype(int)
calendario.mm=calendario.mm.astype(int)
calendario.dd=calendario.dd.astype(int)


colonne=list(range(1,32))
colonne.insert(0,"yy")
colonne.insert(1,"mm")

#i file omogeneizzati giornalieri hanno estensione "v.txt"
filev=glob.glob("*v.txt")

if not len(filev):
    sys.exit("Qualcosa non torna, non trovo i file v.txt")
    
def creaDataFrame(nomeFile):
       
    if len(re.findall("d.txt",nomeFile))==1:
        nomeVariabile="flag"
    else:
        nomeVariabile="tmp"
    
    
    dati=[]
    
    with open(nomeFile,"r") as nf:
            next(nf) #skip header

            for rr in nf.readlines():
                serie=np.array(rr.split(),dtype=float)
                #aggiungiamo gli na dove mancano
                paddedSerie=np.pad(serie,pad_width=(0,33-len(serie)),mode="constant",constant_values=np.nan)
                dati.append(paddedSerie)
                
    finale=np.asarray(dati)        
    df=pd.DataFrame(finale,columns=colonne)
    dfMelted=df.melt(id_vars=["yy","mm"],var_name="dd",value_name=nomeVariabile)
    
    #se si tratta del file "d.txt" trasformiamo i valori in 1 e i valori mancanti in 9
    #ovvero stiamo trasformando i dati originali in flag. I dati originariamente presenti li 
    #manterremo dal file dei dati omogeneizzati, mentre i dati inizialmente mancanti li elimineremo
    if nomeVariabile=="flag":
        #creiamo variabile di appoggio con valori 1 (dato presente nei dati originari) e 9 (dato originariamente mancante)
        dfMelted.loc[(dfMelted.flag < -999) | (pd.isnull(dfMelted.flag)),"app"]=9
        dfMelted.loc[(dfMelted.flag > -999) & (pd.notnull(dfMelted.flag)),"app"]=1
        dfMelted.drop(labels=["flag"],axis=1,inplace=True)
        dfMelted.columns=["yy","mm","dd","flag"]
        dfMelted.flag=dfMelted.flag.astype(int)

  
    dfMelted.yy=dfMelted.yy.astype(int)    
    dfMelted.mm=dfMelted.mm.astype(int)    
    dfMelted.dd=dfMelted.dd.astype(int)        
    
    return dfMelted
        
listaOut=[]   
    
for vv in filev:
    #print("Elaboro {}".format(vv))
    dd=re.sub("v\\.txt","d.txt",vv) #i file d.txt contengono i giornalieri originali
    flag=creaDataFrame(dd)
    dati=creaDataFrame(vv)
 
    if(dati.shape!=flag.shape):
        sys.exit("I due data frame debbono avere stesse dimensioni")
    
    newdf=pd.merge(dati,flag,how="left",on=["yy","mm","dd"])

    #invalido i flag non validi
    newdf.loc[(newdf.flag!=1),["tmp"]]=np.nan
    newdf.yy=newdf.yy.astype(int)
    newdf.drop(labels="flag",axis=1,inplace=True)
    
    #ora leggiamo nome della stazione
    soloHeader=pd.read_csv(vv,nrows=0,header=0)
    codiceStazione=re.sub(" +","",soloHeader.columns.tolist().pop())
    newdf.columns=["yy","mm","dd",codiceStazione]
    listaOut.append(newdf)
    
finale=reduce(lambda x,y: pd.merge(x,y,how="left",on=["yy","mm","dd"]),listaOut)

#ordina secondo anno e mese
finale.sort_values(by=["yy","mm","dd"],inplace=True)


finale=pd.merge(calendario,finale,how="left",on=["yy","mm","dd"])

nomeFileOutput=os.path.split(os.getcwd())[1]
finale.to_csv(nomeFileOutput+".csv",header=True,sep=";",index=False)
