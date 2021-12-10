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


###################


def predictnextText(letter,n):
    df=dfWordCount[dfWordCount["Word"].str.startswith(letter)==True]
    df=df.head(n)
    df=df.reset_index()
    l=list(df["Word"])
    global xvals
    xvals=list(df["Word"])
    global yvals
    yvals=list(df["Freq"])
    return str(l)

def LastChar(text):
    s=text
    l=len(s)
    if((" " in s) == True):
        i = s.rindex(" ")
        return str(s[i+1:l])
    else:
        return str(s[l-1])

def lastword(text):
    lW = word_tokenize(text)
    return lW[len(lW)-1]

def NextWordPred(g,n):
    df=dfw[dfw["Word"]==g]
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


#####################

#def plot(G):


#     #*** Plot Word Cloud ***
#     d = {}
#     for a, x in G.values:
#         d[a] = x
#     print(d)
#     wordcloud = WordCloud(background_color="white")
#     wordcloud.generate_from_frequencies(frequencies=d)
#     plt.figure(figsize=[8,8])
#     plt.imshow(wordcloud, interpolation="bilinear")
#     plt.axis("off")
#     plt.show()


def load(request):
    global FirstFlag
    Inp = request.GET.get('text', 'default')
    # n = request.GET.get('value')
    # return render(request, 'index.html', {n})
    if(FirstFlag==False):
        FirstFlag=True
        compute(3000)#449644
        if (Inp[len(Inp) - 1] != " "):
            P = LastChar(Inp)
            g = predictnextText(P, 9)
            G = {'Gtext': str(g)}
        else:
            W = lastword(Inp)
            g = NextWordPred(W, 9)
            G = {'Gtext': str(g)}
            print(G)
    else:
        if (Inp[len(Inp) - 1] != " "):
            P = LastChar(Inp)
            g = predictnextText(P, 9)
        else:
            W = lastword(Inp)
            g = NextWordPred(W, 9)
    Xval = dumps(xvals)
    Yval = dumps(yvals)
    return render(request, 'index.html',{'Gtext': str(g),'XPlot':Xval,'YPlot':Yval })

# n = request.GET.get('value')
# return render(request, 'index.html', {n})