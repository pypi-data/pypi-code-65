  # -*- coding: utf-8 -*-

ask = 'ghost'
inp = 'dont know'
feel = 'good'
stob = [0, 1 , 2 , 3 , 4]
stog = [6 , 7 , 8 , 9]
ovimo = 'happy'

def emotion (ask, url) :
  from firebase import firebase
  firebase = firebase.FirebaseApplication(url, None)

  inp = 'dont know'

  ovalue = firebase.get('/oi', None)
  ovalue = str(ovalue).replace('None, ', '')
  ovalue = str(ovalue).replace('[', '')
  ovalue = str(ovalue).replace(']', '')
  ovalue = str(ovalue).replace(' ', '')
  ovalue = ovalue.split(',')

  b = firebase.get('/knowlage', None)
  c = str(b).replace('{', '')
  c2 = str(c).replace('}', '')
  c3 = str(c2).replace("'", '')
  c5 = str(c3).replace(' ', '')
  c4 = str(c5).split(',')

  for y in c4:
    compare = y.split(':')
    if ask == compare[0]:
      inp = int(compare[1])

  moodG = ovalue.count('10')
  moodB = ovalue.count('0')

  knowb = bad = sum(stob)/len(stob)
  knowg = good = sum(stog)/len(stog)

  
  if moodG < moodB :
    ovimo = 'Frustrated'

  if moodG > moodB :
    ovimo = 'Happy'

  if moodG == len(ovalue) :
    ovimo = 'Very-Happy'

  if moodB == len(ovalue) :
    ovimo = 'Depressed'

  if moodB == moodG :
    ovimo = 'Moderate'


  # Bad
  if inp > bad and inp<5 :
    feel = 'angry'

  if inp == bad and inp<5 :
    feel = 'sad'

  if inp < 1 and inp<5 :
    feel = 'scared'

  # Good
  if inp > good and inp<10 and inp>5 :
    feel = 'excited'
    

  if inp < good and inp<10 and inp>5 :
    feel = 'happy'


  if inp == good and inp<10 and inp>5 :
    feel = 'h-cited'
    

  if inp == 5 :
    feel = 'nothing'

  if inp == 'dont know':
    val = input("Sorry I don't know about" + inp + " ,but I am Curious about it Can you please tell me, How you feel about it? (give the answer in 'angry','sad','scared','excited','happy','h-cited','nothing' :   "   )
    l = val.lower()
    if l == 'angry':
      kit = 4
      print('Thanks!')
    if l == 'sad':
      kit = 2.0
      print('Thanks!')
    if l == 'scared':
      kit = 0
      print('Thanks!')
    if l == 'excited':
      kit = 8
      print('Thanks!')
    if l == 'happy':
      kit = 6
      print('Thanks!')
    if l == 'h-cited':
      kit = 7.5
      print('Thanks!')
    if l == 'nothing':
      kit = 5
      print('Thanks!')

    input = inp
    emotion = kit
    url = url

    learn(input, emotion, url)





  emotion.feelings = 'I am feeling '+ feel+ ' about ' + ask
  emotion.mood = 'mood:'+ ovimo

def learn (input, emotion, url) :
  
  knoutings= input
  emI = emotion
  from firebase import firebase
  firebase = firebase.FirebaseApplication(url, None)
  firebase.put('/knowlage',knoutings,emI)

  count = firebase.get('/count',None)
  count = str(count).replace('None, ', '')
  count = str(count).replace('[', '')
  count = str(count).replace(']', '')
  count = str(count).replace(' ', '')

  count2 = int(count) + 1

  firebase.put('/count','1',count2)

  print(count2)

  if emI == 0 or 1 or 2 or 3 or 4:
    firebase.put('/oi',count2,0)

  else:
    firebase.put('/oi',count2,10)