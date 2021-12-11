# Imports

import pandas as pd
from matplotlib import pyplot as plt
from nltk.tokenize import word_tokenize
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
from collections import Counter
import string
from django.http import HttpResponse
from django.shortcuts import render
from json import dumps

# global Variables
FirstFlag=False
DC_stopper=False
dfw=pd.DataFrame()
dfWordCount=pd.DataFrame()
xvals=[]
yvals=[]

# Manoj have created this file
def index(request):
    return render(request, 'index.html')

#def home(request):
#    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def Project(request):
    return render(request, 'Project.html')


def feedback(request):
    return render(request, 'project.html')

# main module code R

def pre_Word(arr):
    dfW = pd.DataFrame()
    l = arr.copy()
    del l[-1]
    dfW["Word"] = l
    l = arr.copy()
    del l[0]
    dfW["Before_Word"] = l
    dfW["Freq"] = 0
    return dfW


def compute(n=10000):
    global DC_stopper
    DC_stopper=True
    #*** Read File ***
    f = open('en_US.blogs.txt', 'r', encoding='utf8')  # 9 min to run 899288lines
    strAllTexts = ""
    lines = f.readlines()
    l = len(lines)
    if (n != l):
        del lines[n:l]
    strAllTexts = str(lines)
    f.close()

    # ** Split Text To Words ***
    lstAllWords = word_tokenize(strAllTexts)

    # ** Convert To Lower Case ***
    lstAllWords = [t.lower() for t in lstAllWords]

    # ** Remove Punctuations & Digits ***
    lstAllWords = [t.translate(str.maketrans('', '', '01234567890')) for t in lstAllWords]
    lstAllWords = [t.translate(str.maketrans('', '', string.punctuation)) for t in lstAllWords]

    # ** Remove Profane Words ***
    lstProfWords = ["arse", "ass", "asshole", "bastard", "bitch", "bloody", "bollocks", "child-fucker", "cunt", "damn",
                    "fuck", "goddamn", "godsdamn", "hell", "motherfucker", "shit", "shitass", "whore"]
    lstAllWords = [t for t in lstAllWords if t not in lstProfWords]

    # ** Remove App Specific Words ***
    lstSpecWords = ['ve','ll',' ','’','—','”','“','rt','nt','via','http','https','mailto']
    singleapla="bcdefghjklmnopqrstuvwxyz"
    lstSpecWords=lstSpecWords+list(singleapla)
    lstAllWords = [t for t in lstAllWords if t not in lstSpecWords]

    # *Remove Short Words ***
    lstAllWords = [t for t in lstAllWords if len(t) > 0]

    global dfw
    dfw = pre_Word(lstAllWords)

    # ** Word Freq Count ***
    dctWordCount = Counter(lstAllWords)
    print('Done ...')

    # ** Convert To Dataframe ***
    global dfWordCount
    dfWordCount = pd.DataFrame.from_dict(dctWordCount, orient='index').reset_index()
    dfWordCount.columns = ['Word', 'Freq']
    print('Done ...')

    # *** Word Freq Count - Sorted ***
    dfWordCount = dfWordCount.sort_values('Freq', ascending=False)
    print('Done ...')

    DC_stopper=False


###################


def predictnextText(letter,n):
    df=dfWordCount[dfWordCount["Word"].str.startswith(letter)==True]
    if (len(df) != 0):
        df=df.head(n)
        df=df.reset_index()
        l=list(df["Word"])
        global xvals
        xvals=list(df["Word"])
        global yvals
        yvals=list(df["Freq"])
        return str(l)
    else:
        return "No Predicted Words"

def LastChar(text):
    s=text
    l=len(s)
    if((" " in s) == True):
        i = s.rindex(" ")
        return str(s[i+1:l])
    else:
        return str(s)

def lastword(text):
    lW = word_tokenize(text)
    return lW[len(lW)-1]

def NextWordPred(g,n):
    df=dfw[dfw["Word"]==g]
    if (len(df) != 0):
        dictW=Counter(df["Before_Word"])
        dfWord=pd.DataFrame.from_dict(dictW, orient='index').reset_index()
        dfWord.columns = ['Word','Freq']
        dfWord= dfWord.sort_values('Freq',ascending=False)
        dfWord= dfWord.head(n)
        dfWord= dfWord.reset_index()
        l=list(dfWord["Word"])
        global xvals
        xvals = list(dfWord["Word"])
        global yvals
        yvals = list(dfWord["Freq"])
        return str(l)
    else:
        return "No Predicted Words"

#####################


def load(request):
    global FirstFlag
    global xvals
    global yvals
    xvals=[]
    yvals=[]
    Inp = request.GET.get('text', 'default')
    n=9
    puncFlag=False
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    num="1234567890"
    global DC_stopper
    if(Inp!=""):
        for char in Inp:
            if char in punctuations:
                puncFlag = True
            if char in  num:
                puncFlag = True

        if(puncFlag != True):
            Inp = Inp.lower()
            if(FirstFlag==False):
                compute(100000)#449644
                if(DC_stopper==False):
                    FirstFlag = True
                    if (Inp[len(Inp) - 1] != " "):
                        P = LastChar(Inp)
                        g = predictnextText(P, n)
                        p="Predicting Completion Of Entered Word"
                    else:
                        W = lastword(Inp)
                        g = NextWordPred(W, n)
                        p="Predicting Next Word"
                    if(g!="No Predicted Words"):
                        Xval = dumps(xvals)
                        Yval = dumps(yvals)
                else:
                    g = ""
                    p = "Error:Interupted processing"
                    return render(request, 'index.html',
                                  {'Gtext': str(g), 'Ptext': str(p)})
            else:
                if (Inp[len(Inp) - 1] != " "):
                    P = LastChar(Inp)
                    g = predictnextText(P, n)
                    p="Predicting Completion Of Entered Word"
                else:
                    W = lastword(Inp)
                    g = NextWordPred(W, n)
                    p="Predicting Next Word"

                if (g != "No Predicted Words"):
                    Xval = dumps(xvals)
                    Yval = dumps(yvals)

            if(len(xvals)!=0):
                if(len(xvals)==9):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]), '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '4x': dumps(xvals[3]), '5x': dumps(xvals[4]), '6x': dumps(xvals[5]),
                                   '7x': dumps(xvals[6]), '8x': dumps(xvals[7]), '9x': dumps(xvals[8]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]), '4y': dumps(yvals[3]), '5y': dumps(yvals[4]),
                                   '6y': dumps(yvals[5]), '7y': dumps(yvals[6]), '8y': dumps(yvals[7]), '9y': dumps(yvals[8]),
                                   'N':dumps(n)})
                elif(len(xvals)==8):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '4x': dumps(xvals[3]), '5x': dumps(xvals[4]),
                                   '6x': dumps(xvals[5]),
                                   '7x': dumps(xvals[6]), '8x': dumps(xvals[7]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]), '4y': dumps(yvals[3]),
                                   '5y': dumps(yvals[4]),
                                   '6y': dumps(yvals[5]), '7y': dumps(yvals[6]), '8y': dumps(yvals[7]),
                                   'N':dumps(n)})
                elif (len(xvals) == 7):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '4x': dumps(xvals[3]), '5x': dumps(xvals[4]),
                                   '6x': dumps(xvals[5]), '7x': dumps(xvals[6]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]), '4y': dumps(yvals[3]),
                                   '5y': dumps(yvals[4]), '6y': dumps(yvals[5]), '7y': dumps(yvals[6]),
                                   'N':dumps(n)})
                elif (len(xvals) == 6):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '4x': dumps(xvals[3]), '5x': dumps(xvals[4]),
                                   '6x': dumps(xvals[5]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]), '4y': dumps(yvals[3]),
                                   '5y': dumps(yvals[4]), '6y': dumps(yvals[5]), 'N':dumps(n)})
                elif (len(xvals) == 5):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '4x': dumps(xvals[3]), '5x': dumps(xvals[4]),
                                   '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]), '4y': dumps(yvals[3]),
                                   '5y': dumps(yvals[4]), 'N':dumps(n)})
                elif (len(xvals) == 4):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '4x': dumps(xvals[3]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]), '4y': dumps(yvals[3]),
                                   'N':dumps(n)})
                elif (len(xvals) == 3):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]),
                                   '3x': dumps(xvals[2]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]), '3y': dumps(yvals[2]),'N':dumps(n)})
                elif (len(xvals) == 2):
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '2x': dumps(xvals[1]), '1y': dumps(yvals[0]),
                                   '2y': dumps(yvals[1]),'N':dumps(n)})
                else:
                    return render(request, 'index.html',
                                  {'Gtext': str(g),'Ptext': str(p), 'XPlot': Xval, 'YPlot': Yval, '1x': dumps(xvals[0]),
                                   '1y': dumps(yvals[0]),'N':dumps(n)})
            else:
                p = "-"
                return render(request, 'index.html',
                              {'Gtext': str(g), 'Ptext': str(p)})
        else:
            g = "Input should Not contain Numbers or special Characters"
            p = "Error:Input Type"
            return render(request, 'index.html',
                          {'Gtext': str(g), 'Ptext': str(p)})
    else:
        g=""
        p="Error:Empty Input"
        return render(request, 'index.html',
                      {'Gtext': str(g),'Ptext': str(p)})