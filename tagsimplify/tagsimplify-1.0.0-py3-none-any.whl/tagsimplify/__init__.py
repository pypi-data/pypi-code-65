
import re

#deal with taggs--> like <html> the </html> <html> of </html> -->
#<html> the of </html>

def tag_postprocessing(ret):
    outside=""
    inside=False
    se=[]
    sent=[]
    count=0
    mre=""
    mmre=""
    #print("len...",len(ret))
    length=len(ret)-1
    for indexx,ii in enumerate(ret):
        #print("indexx...",indexx ,ii)
        if '\n'in ii :
            #print("yes")
            if indexx-1 == sent[-1]:
                pass
            else: 
                sen=mmre
                sent.append(sen)
            count_slashN=ii.count('\n')
            #print("slash n count...",count_slashN)
            #print("slash n...",indexx, "#print...",ii ,len(ii))
            #count_slashN=len(ii)
            #print("slash nn...",indexx, "#print...",count_slashN)
            if count_slashN==1:
                
                sent.append('\n')
            else:    
                #count_slashN=count_slashN-3
                sent.append('\n'*count_slashN)
            count=1
        
        else:    
            for index,i in enumerate(ii.split()):
                #print("ii.....",i)
                m=re.match('<[A-Z]*>',i)
                mm=re.match('</[A-Z]*>',i)
                
                if m==None and mm==None and inside==False and outside=="":
                    sen=i+" "
                    sent.append(sen)
                    ##print("sen1....",sent)
                    f=' '.join(sent)
                    #print("f1.....",f)
                elif m!=None and mm==None and inside==False and outside=="":
                    mre=m.group(0)
                    count=0
                    if mre in se:
                        if sent[-1]==("." or ","):
                           sen=mre
                           sent.append(sen)
                           ##print("sen2....",sent)
                           f=' '.join(sent)
                           #print("f2.....",f)
                           inside=True
                        else:
                           #sent[-1]=""
                           ##print("sen22....",sent)
                           f=' '.join(sent)
                           #print("f22.....",f)
                           inside=True
                    elif mre not in se:
                        se=[]
                        se.append(mre)
                        sen=i+" "
                        sent.append(sen)
                        ##print("sen3....",sent)
                        f=' '.join(sent)
                        #print("f3.....",f)
                        inside=True     
                elif m==None and mm!=None and inside==True   and outside=="":
                    mmre=mm.group(0)
                    inside=False
                    outside="begin"
                    if indexx==length:
                        sen=i
                        sent.append(sen)
                    ##print("sen5....",sent)
                    else:
                        f=' '.join(sent)
                        #print("f5.....",f)
                elif m==None and mm==None and inside==True and count==1  and outside=="":
                    sent.append('\n')   
                elif m==None and mm==None and inside==True and count==0 and outside=="":
                   
                    if sent[-1]==mmre:
                        sent[-1]=""
                        #sen=' '.join(temp)
                        sen=i
                        sent.append(sen)
                        ##print("sen4....",sent)
                        f=' '.join(sent)
                        #print("f4.....",f)
                    else:
                        sen=i+" "
                        sent.append(sen)
                        ##print("sen44....",sent)
                        f=' '.join(sent)
                        #print("f44.....",f)
                
                
                   
                elif m==None and mm==None  and inside==False and outside=="begin":
                    sen=mmre
                    sent.append(sen)
                    sen=i
                    sent.append(sen)
                    outside=""
                    se=[]
                    ##print("sen6....",sent)
                    f=' '.join(sent)
                    #print("f6.....",f)
                elif m!=None and mm==None and inside==False and outside=="begin":
                    outside=""
                    inside=True
                    mre=m.group(0)
                    if mre not in se:
                        sen=mmre
                        sent.append(sen)
                        se=[]
                        se.append(mre)
                        sen=mre+" "
                        sent.append(sen)
                        mmre=""
                    ##print("sen7....",sent)
                    f=' '.join(sent)
                    #print("f7.....",f)
                elif m==None and mm!=None and inside==False and outside=="": 
                    mmre=mm.group(0)
                    sen=mmre
                    sent.append(sen)
                    ##print("sen8....",sent)   
                    f=' '.join(sent)
                    print("f8.....",f)
                
    return sent       

#deal with blank line
    
def blank_postprocessing(sent):
    sentence=[]
    blank=""
    for index,w in enumerate(sent):
        #print(index)
        n=re.match('<[A-Z]*>',w)
        nn=re.match('</[A-Z]*>',w)
        if '\n'in w :        
            count_sent_slashN=w.count('\n')
            sentence.append('\n'*count_sent_slashN)
            blank="start"
        if n!=None and nn==None and blank=="":     
            #print("w...",w)
            sentence.append(w)
        elif n==None and nn!=None and blank=="":
            #print("w1....",w)
            sentence.append(w)
        elif n==None and nn==None and blank=="":
            #print("w2....",w)
            if w=='':
                sentence.append(w)
            else:
                sentence.append(w)
        elif n!=None and nn==None and blank=="start":
            #print("w3....",w)
            if sentence[-1]!='\n'*count_sent_slashN:
                sentence.append(w)
            else:  
                #print("w3..yes..",w)
                #sentence.append('\n'*count_sent_slashN)
                sentence.append(w)
            blank=""
        elif n==None and nn!=None and blank=="start":
            #print("w4...",w)
            if sentence[-1]=='\n'*count_sent_slashN:
                #print("w6...yes")
                sentence[-1]=w
                sentence.append('\n'*count_sent_slashN)
            else:    
                sentence.append(w)
                sentence.append('\n'*count_sent_slashN)
            blank=""
        elif n==None and nn==None and blank=="start":
            #print("w5...",index,w)
            if '\n'in w :
                pass
                
            else:
                #print("w55...",index,w)
                sentence.append(w)   
                
    sent_file=' '.join(sentence)    
    return sent_file

   
#deal with --> <html> the </html> --> <html>the</html>
# <html> the of </html> --> <html>the of</html>      
''' 
def text_postprocessing(ret):
    
        sent=tag_postprocessing(ret)
        sent_file=blank_postprocessing(sent)
        #sent_file=ret
        regex = r"<[A-Z]*>\s(.*?)\s</[A-Z]*>"
        matches = re.finditer(regex, sent_file, re.MULTILINE)
        s5=""
        s3=""
        for matchNum, match in enumerate(matches, start=1):    
            
            s1=match.group() 
            #print(s1)
            s2=len(s1.split())
            #print(s2)
            if s2==3:
                for index, i in enumerate(s1.split()):
                    if index==0:
                        s3+=i
                    else:
                        s3+=i
            else:
                for index, i in enumerate(s1.split()):
                    if index==0:
                        #print("y1")
                        #print(index,i)
                        s3+=i
                        #print(s3)
                    elif index==1:
                        #print("y2")
                        #print(index,i)
                        s3+=i+" "
                        #print(s3)
                    elif  index==s2-2:
                        #print("y3")
                        #print(index,i)
                        s3+=i
                        #print(s3)
                    
                    else:
                        #print("y5")
                        #print(index,i)
                        s3+=i+' '
                        #print(s3)
            if matchNum==1:
                s4=sent_file.replace(s1,s3)
                s3=""       
                #print("s42...",s4)
            else:
                s5=s4.replace(s1,s3)
                s3=""       
                #print("s43...",s5)
                s4=s5
        #print("sent_file....",sent_file)
        if s5=='':
            return s4
        else :
            return s5 

'''        

    
   



def text_postprocessing(ret):
    
    if type(ret)==list:
        sent=tag_postprocessing(ret)
        sent_file=blank_postprocessing(sent)
        #sent_file=ret
        #print("sent_file...",sent_file)
        regex = r"<[A-Z]*>\s(.*?)\s</[A-Z]*>"
        matches = re.finditer(regex, sent_file, re.MULTILINE)
        s5=""
        s3=""
        for matchNum, match in enumerate(matches, start=1):    
            
            s1=match.group() 
            #print(s1)
            s2=len(s1.split())
            #print(s2)
            if s2==3:
                for index, i in enumerate(s1.split()):
                    if index==0:
                        s3+=i
                    else:
                        s3+=i
            else:
                for index, i in enumerate(s1.split()):
                    if index==0:
                        #print("y1")
                        #print(index,i)
                        s3+=i
                        #print(s3)
                    elif index==1:
                        #print("y2")
                        #print(index,i)
                        s3+=i+" "
                        #print(s3)
                    elif  index==s2-2:
                        #print("y3")
                        #print(index,i)
                        s3+=i
                        #print(s3)
                    
                    else:
                        #print("y5")
                        #print(index,i)
                        s3+=i+' '
                        #print(s3)
            if matchNum==1:
                s4=sent_file.replace(s1,s3)
                s3=""       
                #print("s42...",s4)
            else:
                s5=s4.replace(s1,s3)
                s3=""       
                #print("s43...",s5)
                s4=s5
        #print("sent_file....",sent_file)
        if s5=='':
            return s4
        else :
            return s5 

            
    raise TypeError("Input should be list")
    

