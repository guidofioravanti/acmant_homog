#elabora i risultati dell'omogeneizzazione: applica  i flag ai file mensili e costruisce un dataframe unico con tutte le
#serie nel cluster

import glob
import sys
import numpy as np
import pandas as pd
import re
import pdb
from functools import reduce
import os

colonne=list(range(1,13))
colonne.insert(0,"yy")


filej=glob.glob("*j.txt")

if not len(filej):
    sys.exit("Qualcosa non torna")
    
def creaDataFrame(nomeFile):
    
    if len(re.findall("j.txt",nomeFile))==1:
        tipoDati=int
        nomeVariabile="flag"
    else:
        tipoDati=float
        nomeVariabile="tmp"
    
    try:
        serie=np.loadtxt(nomeFile,skiprows=1,dtype=tipoDati)
    except:
        sys.exit("Impossibile aprire file {}".format(nomeFile))
    
    df=pd.DataFrame(serie,columns=colonne)
    return df.melt(id_vars="yy",var_name="mm",value_name=nomeVariabile)
        
listaOut=[]    
    
for jj in filej:
    tt=re.sub("j\\.txt","t.txt",jj)
    flag=creaDataFrame(jj)
    dati=creaDataFrame(tt)
    
    if(dati.shape!=flag.shape):
        sys.exit("I due data frame debbono avere stesse dimensioni")
    
    newdf=pd.merge(dati,flag,how="left",on=["yy","mm"])
    #invalido i flag non validi
    newdf.loc[(newdf.flag!=1) & (newdf.flag!=2),["tmp"]]=np.nan
    newdf.yy=newdf.yy.astype(int)
    newdf.drop(labels="flag",axis=1,inplace=True)
    
    #ora leggiamo nome della stazione
    soloHeader=pd.read_csv(jj,nrows=0,header=0)
    codiceStazione=re.sub(" +","",soloHeader.columns.tolist().pop())
    newdf.columns=["yy","mm",codiceStazione]
    listaOut.append(newdf)
    
finale=reduce(lambda x,y: pd.merge(x,y,how="left",on=["yy","mm"]),listaOut)

#ordina secondo anno e mese
finale.sort_values(by=["yy","mm"],inplace=True)

nomeFileOutput=os.path.split(os.getcwd())[1]
finale.to_csv(nomeFileOutput+".csv",header=True,sep=";",index=False)
