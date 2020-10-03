#This is the list of all the functions for this project. This could change as the package is currently unstable.

#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# Invoke Libraries
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
import pandas as pd
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# Build  Functions
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

#function to remove punctuation
def remov_punct(withpunct):
    punctuations = set(['!','(',')','-','[',']','{','}',';',':',',','<','>','.','/','?','@','#','$','%','^','&','*','_','~',"\\"])
    without_punct = ""
    char = 'nan'
    for char in withpunct:
        if char not in punctuations:
            without_punct = without_punct + char
    return(without_punct)

#Retrieve the POS tag
def ptb_to_wn(tag):    
    if tag.startswith('N'):
        return 'n' 
    if tag.startswith('V'):
        return 'v' 
    if tag.startswith('J'):
        return 'a' 
    if tag.startswith('R'):
        return 'r' 
    return None


def tagged_to_synset(word, tag):
    wn_tag = ptb_to_wn(tag)
    if wn_tag is None:
        return None 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None
    
    
def sentence_similarity(s1, s2):        
    s1 = pos_tag(word_tokenize(s1))
    s2 = pos_tag(word_tokenize(s2)) 
    
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in s1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in s2]
 
    #suppress "none"
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
        
    scoreList = list()
    
    for i in range(0,len(synsets1)):           
        best_score = max([synsets1[i].path_similarity(ss) for ss in synsets2])                
        scoreList.append(best_score)    
    
    #drop None values if any from the list
    scoreListUpdated = [i for i in scoreList if i]
    
    #average the best_score values
    avgScore = (sum(scoreListUpdated)/len(scoreListUpdated))   

    return(avgScore)

#compute the symmetric sentence similarity
def symSentSim(s1, s2):     
    try:
        sssScoreSide1 = sentence_similarity(s1, s2)                                              
    except:        
        sssScoreSide1 = 0        
    
    try:
        sssScoreSide2 = sentence_similarity(s2, s1)                                              
    except:        
        sssScoreSide2 = 0       
    
    sss_score = (sssScoreSide1 + sssScoreSide2)/2        

    return (sss_score)

