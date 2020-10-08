#!/usr/bin/env python3
from os import path as p, rename as r
import logging

class propHandler(object):
  start_par=':'
  end_par='\n'
  log_file=logging.getLogger('propHandler')
  log_path='./misc/storedata/log.log'
  FORMAT = '%(asctime)-15s %(thread)d %(threadName)s %(clientip)s %(user)-8s %(levelname)s: %(message)s'
  d = {'clientip':'local', 'user':'GHOST'}

  def __init__(self, pathToLog:str = None, className:str = None):
    self.log_path = p.join(pathToLog, 'log.log')
    logging.basicConfig(filename=self.log_path, format=self.FORMAT)
    if not className:
      self.log_file = logging.getLogger(self) 
    else:
      self.log_file = logging.getLogger(className)
  
  def log(self, lvl:str = 'debug', msg:str = '', clientip:str='local', user:str='GHOST'):
    temp_d = { **self.d, 'clientip': clientip, 'user':user}
    if lvl.lower() in ('info', 'debug', 'warning', 'error','critical'):
      self.log_file.log(level=lvl, msg=msg, extra=temp_d)
  
  def error(self, msg:str):
    self.log_file.exception(msg)

  def store_par_line(self, file_path:str = None, parName:str = None, parValue:str = None) -> bool:
    if not file_path and not parName and not parValue:
      self.log(msg='file_path, parName and parValue not null')
      try:
        with open(file_path, 'rb') as file:
          self.log(msg='retrieve lines in file_path')
          lines=file.readlines()
        indices = [i for i, elem in enumerate(lines) if parName+self.start_par in elem]
        self.log(msg='create indices for popping out the list (if the file is already inserted)')
        for i in indices:
          lines.pop(i)
        line=parName.lower()+self.start_par+parValue+self.end_par
        lines.append(line)
        try:
          with open(file_path, 'wb') as file:
            self.log(msg='write on files')
            file.writelines(lines)
          self.log(lvl='info', msg='parameter stored successfully')
          return True
        except Exception as er:
          self.error(('Error occured writing file stored in %s, %s' % file_path, er.__traceback__.__str__))
          return False
      except Exception as e:
        self.error(('Error occured open file stored in %s, %s' % file_path, e.__traceback__.__str__))
        return False
    else:
      self.log(lvl='warning', msg='parameter has not being stored, it may raise an exception later!')
      return False

  def get_par_line(self, file_path:str=None, parName:str=None):
    if not file_path:
      if not parName:
        try:
          with open(file_path,'rb') as file:
            for line in file:
                self.log(lvl='info', msg=('parameter %s has being retrieved' % parName))
                return line.split(self.start_par)[1]
            self.log(lvl='error', msg=('parameter %s has not being retrieved, error' % parName))
            return ('Error: %s not found!' % parName)
        except Exception as e:
          self.error(('Error occured open file stored in %s, %s' % file_path, e.__traceback__.__str__))
      else:
        self.log(lvl='error', msg='parName cannot be empty!')
        return 'Error: ParName is empty!'
    else:
      self.log(lvl='error', msg='file_path cannot be empty!')
      return 'Error: file_path is empty!'

  @staticmethod
  def get_path(file_name:str) -> str:
    return p.join(p.dirname(p.realpath(__file__)), file_name)

  def rename_file(self, pathA:str, pathB:str, pathRoot:str) -> bool:
    try:
      file1=p.join(pathRoot,pathA)
      file2=p.join(pathRoot,pathB)
      r(file1,file2)
      self.log(lvl='info', msg=('File %s now %s' % pathA, pathB))
      return True
    except Exception as e:
      self.error(('Exception: %s' % e.__traceback__.__str__))
      return False