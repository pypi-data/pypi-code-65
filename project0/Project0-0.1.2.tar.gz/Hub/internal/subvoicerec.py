#!/usr/bin/env python3
from . import prophandler as ph
from threading import Thread
import speech_recognition as sr
import pyttsx3 as tts
import time
try:
  from queue import Queue
except ImportError:
  from Queue import Queue

# NOTE: this class requires PyAudio because it uses the Microphone class
class VoiceRecHub:
  #Class Attribute
  ### Wav saving file position
  audio_queue = Queue()
  ### Voice Intonation file position
  voice_path:str = './misc/storedata/intonation.voiceRecHub'
  ### PropertyFile inspection
  propPath:str = './misc/storedata/property.voiceRecHub'
  ### PropertyHandler Class
  prop: ph.propHandler()
  ### Private Server 
  server: None

  def __init__(self):
    pathToLog = self.prop.get_path('log.log')
    intonationVoicePath = self.prop.get_path('Intonation.voice')
    self.prop = ph.propHandler(pathToLog=pathToLog, className='VoiceRecHub')
    self.prop.log(msg='Inizio creazione classe VoiceRecHub')
    self.voice_path = intonationVoicePath
    self.audio_file = self.prop.get_path('temp.wav')
    
  #Function - Compute the audio File
  def compute_audio(self, online:bool, audio, language:str, clientIP:str = None, clientID:str = None) -> str:
    # use the audio file as the audio source
    r = sr.Recognizer()
      
    with sr.AudioFile(audio) as source:
      r.pause_threshold = 3.0
      r.adjust_for_ambient_noise(source, duration=3)
      a = r.record(source)
    try:
      if online:
        command = r.recognize_sphinx(a, language=language)
      else:
        command = r.recognize_google(a, language=language)
      message = 'sphinx ha capito {0}'+command
      if not clientIP and not clientID:
        self.prop.log(msg=message, clientip=clientIP, user=clientID)
        return self.chunckMsgAndDecode(command,clientIP,clientID)
      else:
        self.prop.log(msg=message)
        return self.chunckMsgAndDecode(command)
    except sr.UnknownValueError as s:
      lvl='warning'
      if not clientIP and not clientID:
        msg='sphinx could not understand audio from client\n{0}'.format(s)
        self.prop.log(lvl, msg, clientip=clientIP, user=clientID)
        return '!cmd'
      else:
        self.prop.log(lvl, msg='sphinx could not understand audio\n{0}'.format(s))
        return '!cmd'
    except sr.RequestError as e:
      lvl='warning'
      msg='sphinx error:\n{0}'.format(e)
      if not clientIP and not clientID:
        self.prop.log(lvl, msg, clientip=clientIP, user=clientID)
        return '!cmd'
      else:
        self.prop.log(lvl, msg)
        return '!cmd'

  def chunckMsgAndDecode(self, command:str, clientip:str='local', user:str='GHOST') -> str:
    # For now, return only the command spoken, later, try to understand the single istance 
    # and to submit the correct external (or internal) command
    return command

  def recognize_worker(self, language) -> str:
    # This running in a background thread
    while True:
      audio = self.audio_queue.get()
      if audio is None : break

      try:
        # first locally
        cmd = self.compute_audio(False, audio, language)
        if cmd is not '!cmd':
          self.audio_queue.task_done()
          return cmd
        else:
          # check if the user has abilitate the google audio sending
          google = self.prop.get_par_line(self.propPath, 'GoogleAllowed')
          #check if the system is online
          online = False
          #check private server
          if online:
            cmd = '!cmd'
            if audio is not '!cmd':
              self.audio_queue.task_done()
              return cmd
            elif google:
              cmd = self.compute_audio(True, audio, language, 'local', 'GHOST')
              if cmd is not '!cmd':
                self.audio_queue.task_done()
                return cmd
              else:
                self.prop.log(lvl='warning', msg='Error Processing audio')
                self.audio_queue.task_done()
                return None
      except Exception as e:
        self.prop.log(lvl='warning', msg='Error Processing audio\n{0}'.format(e))
        self.audio_queue.task_done()
        return None
  
  #Function - Obtain Audio from microphone and queue to audio_file
  def listento_subroutine(self, language):
    r = sr.Recognizer()
    rec_thread = Thread(target=self.recognize_worker(language))
    rec_thread.daemon = True
    rec_thread.start()
    with sr.Microphone() as source:
      r.pause_threshold = 3.0
      r.adjust_for_ambient_noise(source, duration=3)
      try:
        while True:
          self.audio_queue.put(r.listen(source)) # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
      except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass
    self.audio_queue.join()     # block until all current audio processing jobs are done
    self.audio_queue.put(None)  # tell the recognize_thread to stop
    rec_thread.join()           # wait for the recognize_thread to actually stop