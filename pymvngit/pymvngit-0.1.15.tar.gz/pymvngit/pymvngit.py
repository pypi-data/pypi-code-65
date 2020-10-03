#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A tool manager for GIT and/or MAVEN folders

@author: Ualter Otoni Pereira
ualter.junior@gmail.com

"""

import os, sys, configparser, logging, re
import xml.etree.ElementTree as ET
from os.path import expanduser
from pathlib import Path
from urllib.request import pathname2url
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from pymvngit.pygit import PyGit
from pymvngit.console import Console
from pymvngit.utils import Utils, Colors, Emoticons
from pymvngit.prettytable import PrettyTable
from pymvngit.tableargs import TableArgs

__author__    = "Ualter Otoni Pereira"
__copyright__ = "Ualter Otoni Pereira"
__license__   = "MIT"

_logger = logging.getLogger("app." + __name__)
_logger.setLevel(logging.INFO)

GIT = "git"
MAVEN = "maven"
NAME_DB_MACROS = "macros.json"
USER_DIR = os.path.join(expanduser("~"),".pymvngit")
LOG_DIR  = os.path.join(USER_DIR,"logs")
DB_PATH_PROJECT = os.path.join(USER_DIR,"#.json")
DB_PATH_MACRO  = os.path.join(USER_DIR,NAME_DB_MACROS)
INI_FILE = os.path.join(USER_DIR,"pymvngit.ini")

class PyMvnGit:
    '''
    A Python tool to manage Git and/or Maven folders
    __author
    '''

    def __init__(self):
        self._databaseProject   = None
        self._databaseMacro     = None
        self._configIni         = None
        self._connectedDatabase = False
        self._init()

        self._fileDBProject = DB_PATH_PROJECT.replace("#",self._currentDirEncoded())
        self._fileDBMacro   = DB_PATH_MACRO

    def _init(self):
        if not os.path.exists(USER_DIR):
            os.makedirs(USER_DIR)
        self._initLog()
        self._initIniFile()

    def _initLog(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        logging.Formatter("%(asctime)s [%(threadName)-12.12s][%(levelname)-5.5s]  %(message)s")

    def _initDBMacroDefault(self):
        createDefault = False
        if len(self._databaseMacro.all()) == 0:
            createDefault = True

        if createDefault:   
            self._databaseMacro.insert({
                "key":"status",
                "description": "Git Status all projecs",
                "executions":[
                    {
                        "tool":"git",
                        "command":"status",
                        "projects":[]
                    }
                ]
            })

            self._databaseMacro.insert({
                "key":"install_commons",
                "description": "Build and install enrollment client locally",
                "executions":[
                    {
                        "tool":"maven",
                        "command":"clean install",
                        "projects":["teachstore-commons"]
                    },
                    {
                        "tool":"git",
                        "command":"-a push -r commons -b develop -cm $1",
                        "projects":["teachstore-commons"]
                    }
                ]
            })

            self._databaseMacro.insert({
                "key": "all-once",
                "description": "Git Status Add Commit Push ",
                "executions": [
                    {
                        "tool": "git",
                        "command": "status",
                        "projects": ["teachstore-commons","teachstore-enrollment-client"]
                    },
                    {
                        "tool": "git",
                        "command": "add $1",
                        "projects": ["teachstore-commons","teachstore-enrollment-client"]
                    },
                    {
                        "tool": "git",
                        "command": "commit -m $2",
                        "projects": ["teachstore-commons","teachstore-enrollment-client"]
                    },
                    {
                        "tool": "git",
                        "command": "push",
                        "projects": ["teachstore-commons","teachstore-enrollment-client"]
                    },
                    {
                        "tool": "git",
                        "command": "tag -a $3 -m $4",
                        "projects": ["teachstore-commons"]
                    }
                ]
            })


    def _initIniFile(self):
        if os.path.exists(INI_FILE):
           self._configIni = configparser.ConfigParser(allow_no_value=True)
           self._configIni.read(INI_FILE)
        else:
           self._configIni = configparser.ConfigParser(allow_no_value=True) 
           self._configIni.add_section("GENERAL")
           with open(INI_FILE,'w') as c:
               self._configIni.write(c)
           self._configIni = configparser.ConfigParser(allow_no_value=True)
           self._configIni.read(INI_FILE)    

    def _initDBProject(self):
        createIt = True
        if os.path.exists(self._fileDBProject):
           createIt = False
           Console.warning("The repository {}{}{} already exists!".format(Colors.IGREEN,self._currentDir(),Colors.RESET))
           response = input("     {nc}This would recreated it, would you like to proceed ? [{c1}Y{nc}/{c1}N{nc}]: ".format(c1=Colors.IGREEN, nc=Colors.GREEN))
           response = response.upper()
           if "Y" == response:
               self._databaseProject.close()
               self._databaseProject.close()
               os.remove(self._fileDBProject)
               self._connectDBs(startDatabases=True)
           else:
               print("     Ok, bye!\n")
               sys.exit()    
        else:       
           self._connectDBs(startDatabases=True)       

    def _connectDBs(self, startDatabases=False):
        if not os.path.exists(self._fileDBProject) and not startDatabases:
           # Check Environment Variable:
           if 'PYMVNGIT_REPO' in os.environ and os.environ['PYMVNGIT_REPO'] != "":
              defaultRepository = os.environ['PYMVNGIT_REPO']
              foundRepo = False
              for path in Path(USER_DIR).rglob('*.json'):
               if path.name != NAME_DB_MACROS:
                  nameRepo = path.name[path.name.rfind("_")+1:].replace(".json","").lower()
                  if defaultRepository.lower().strip() == nameRepo.strip():
                     self._fileDBProject = DB_PATH_PROJECT.replace("#",path.name.replace(".json","")) 
                     foundRepo = True
                     break
              if not foundRepo:      
                 Console.error(Colors.GREEN + "The environment variable value \"PYMVNGIT={}{}\" was not found as a created repository!".format(Colors.IBLUE + defaultRepository + Colors.RESET, Colors.GREEN))   
                 sys.exit()    
           else:
              direc = self._decodeDirectoryName(self._fileDBProject)
              Console.clear()
              Console.error("{green}There's no repository created at the \n       current directory {iblue}{curdir}{green} \
                            \n\n       Please start it using: {iblue}pymvngit {iyellow}start{green}  \
                            \n\n       {magenta}OR -->{reset}  \
                            \n\n       {green}Set a repository using an environment variable: \
                            \n           {iyellow}export{green} PYMVNGIT_REPO{reset}={iblue}teachstore{green}  \
                            \n\n       {magenta}OR -->{reset} \
                            \n\n       {green}Choose a {iyellow}number{green} below:". \
                            format(curdir=direc,iblue=Colors.IBLUE,green=Colors.GREEN,blue=Colors.BLUE,\
                                   reset=Colors.RESET,magenta=Colors.IMAGENTA,iyellow=Colors.IYELLOW), False)
              #os.environ['HOME']  
              index = 0
              options = []
              print(Colors.RESET + "       +----------------------------------+")
              for path in Path(USER_DIR).rglob('*.json'):
               if path.name != NAME_DB_MACROS:
                  options.append(path.name)
                  nameDecoded = self._decodeDirectoryName(path.name)
                  nameRepo    = nameDecoded
                  if nameDecoded.rfind("/") > 1:
                     nameRepo    = nameDecoded[nameDecoded.rfind("/")+1:]
                  index += 1
                  line = "       {green}[{iblue}{idx:02d}{green}]{reset} - {green}{repo}{reset}" \
                         .format(idx=index,repo=nameRepo,green=Colors.GREEN,iblue=Colors.IBLUE,reset=Colors.RESET)
                  print(line)
              print(Colors.RESET + "       +----------------------------------+")    
              read = input(Colors.IGREEN + "       Number...: ")
              print("")
              if read != "":
                 n = options[int(read)-1].replace(".json","")
                 self._fileDBProject = DB_PATH_PROJECT.replace("#",n)
              else:   
                 sys.exit()              
   
        self._databaseProject = TinyDB(self._fileDBProject, indent=4)
        self._databaseMacro = TinyDB(self._fileDBMacro, indent=4)

        self._initDBMacroDefault()

    def _currentDirEncoded(self):
        nameCurrentDirEncoded = self._encodeDirectoryName(self._currentDir()).replace(":","drive_")
        logging.info("nameCurrentDirEncoded=" + nameCurrentDirEncoded)
        return nameCurrentDirEncoded
    def _currentDir(self):
        currentDirectory = os.getcwd()
        #For testing/development
        # return /dir/dir/dir
        return currentDirectory

    def _encodeDirectoryName(self, directory):
        return directory.replace("\\","_").replace("/","_").replace(":","_drive_").lower()
    def _decodeDirectoryName(self, directory):
        return directory.replace("_","/").replace("_","/").replace("//","/").replace("_drive_",":") \
                        .replace(USER_DIR,"").replace(".json","").lower()    

    def listMacros(self, summary=False, jsonFormat=False):
        """
        \033[0;32mList all the macros available\033[0;0m

        \033[0;32mParameters:\033[0;36m
           jsonFormat (bool): Show in JSON format or a ASCII list

        \033[0;32mReturns:\033[0;36m
           string:Printing results
        \033[0;0m   
        """
        if not self._connectedDatabase:
           self._databaseMacro = TinyDB(self._fileDBMacro, indent=4)

        records = self._databaseMacro.all()
        if jsonFormat:
           Utils.printJSON(Utils.dictToJSON(records))
        else:
           tableArgs   = TableArgs()
           if summary:
              header      = ["#","Key","Description","Executions","Projects"]
              prettyTable = PrettyTable(header)
              idx_lin     = 1
              for r in records:   
                  tools = ""
                  i     = 0
                  for execution in r["executions"]:
                      i += 1
                      tools += "{high}#{i}{co}[{cn}{tool}{co}:{cn}\"{carg}{cmd}{cn}\"{co}]{cn} " \
                               .format(i=i,tool=execution["tool"],cmd=execution["command"], \
                               co=Colors.IBLUE,cn=Colors.GREEN,high=Colors.IGREEN,carg=Colors.CYAN)      
                      projects=", ".join(execution["projects"])
                      if projects == "": projects = "ALL" 
                  
                  columns  = [str(idx_lin), r["key"], r["description"],tools,projects]
                  prettyTable.addRow(columns)
                  idx_lin    += 1
   
              if idx_lin > 1:
                 prettyTable.sortByColumn(0)   
                 prettyTable.numberSeparator = True
                 prettyTable.ascendingOrder(True)
                 Console.printTable("{}MACROS{}".format(Colors.WHITE, Colors.GREEN), prettyTable, tableArgs)    
              else:
                 Console.printLine("No macro found!")
           else:   
              Console.printHeaderCommand("{}MACROS repository: {}".format(Colors.RESET,Colors.IGREEN + self._currentDir() + Colors.GREEN))  
              for r in records:
                  header      = ["Tool/Command","Projects"]
                  prettyTable = PrettyTable(header)
                  idx_lin     = 1
                  i           = 0
                  for execution in r["executions"]:
                      i += 1
                      tool = "{high}#{i}-{co}[{cn}{tool}{co}:{cn}\"{carg}{cmd}{cn}\"{co}]{cn} " \
                               .format(i=i,tool=execution["tool"],cmd=execution["command"], \
                               co=Colors.IBLUE,cn=Colors.GREEN,high=Colors.IGREEN,carg=Colors.CYAN)

                      projects=", ".join(execution["projects"])
                      if projects == "": projects = "ALL" 

                      columns  = [tool, projects]
                      prettyTable.addRow(columns)
                      idx_lin    += 1
                  prettyTable.sortByColumn(0)   
                  prettyTable.numberSeparator = True
                  prettyTable.ascendingOrder(True)
                  Console.printTable2("MACRO: {igreen}{key}{green} - {cyan}{desc}{reset}". \
                      format(key=r["key"],desc=r["description"],igreen=Colors.IGREEN,green=Colors.GREEN,cyan=Colors.CYAN,reset=Colors.RESET), prettyTable, tableArgs)             

        self._databaseMacro.close()
   
    def listProjects(self, jsonFormat=False):
        """
        \033[0;32mList all the projects added to this repository\033[0;0m

        \033[0;32mParameters:\033[0;36m
           jsonFormat (bool): Show in JSON format or a ASCII list

        \033[0;32mReturns:\033[0;36m
           string:Printing Projects
        \033[0;0m   
        """

        for path in Path(USER_DIR).rglob('*.json'):
            if path.name != NAME_DB_MACROS:
               db      = TinyDB(path, indent=4)   
               records = db.all()
               if jsonFormat:
                  Utils.printJSON(Utils.dictToJSON(records))
               else:
                  tableArgs   = TableArgs()
                  header      = ["#","Name","Path","Maven","Git"]
                  prettyTable = PrettyTable(header)
                  idx_lin     = 1
                  for r in records:
                      columns  = [str(idx_lin), r["name"], r["path"], r["maven"], r["git"]]
                      prettyTable.addRow(columns)
                      idx_lin += 1
       
                  prettyTable.sortByColumn(0)   
                  prettyTable.numberSeparator = True
                  prettyTable.ascendingOrder(True)
                  nameDecoded = self._decodeDirectoryName(path.name)
                  nameRepo    = nameDecoded
                  if nameDecoded.rfind("/") > 1:
                     nameRepo    = nameDecoded[nameDecoded.rfind("/")+1:]
                  Console.printTable("NAME:{}{}{} - FOLDER:{}{}{}" \
                         .format(Colors.IGREEN,nameRepo,Colors.RESET, \
                                 Colors.IGREEN,nameDecoded,Colors.GREEN 
                                ), prettyTable, tableArgs)    
               db.close()   

    def clone(self, repositories, localPath, branchName,isRepoListFile):
        args = []
        args.append(repositories)
        args.append(localPath)
        args.append(branchName)
        args.append(isRepoListFile)
        pygit = PyGit("clone",args,None) 
        pygit.execute()

        # Create Repository for the Clone
        self._fileDBProject = DB_PATH_PROJECT.replace("#",self._encodeDirectoryName(localPath))
        self._connectDBs(True)
        if pygit.response:
           for r in pygit.response:
               exist = False if len(self._databaseProject.search(where('name') == r["name"])) == 0 else True
               # Do not include duplicated (most likely the folder was delete but the database entry not)
               if not exist:
                  self._createModule(r["name"],r["path"],r["git"],r["maven"])

    def start(self):
        """
        Creates a repository represeting the Maven/Git projects to be manage together.

        All the subfolder will be analyzed and check if it is a Maven Project and/or a Git Repository. And if it does (one or another),
        it will be added to the PyMvnGit repository.
        """
        self._initDBProject()
        currentDirectory = self._currentDir()

        # Save the current folder as part of the repository
        isMaven = os.path.exists( os.path.join(currentDirectory,"pom.xml") )
        isGit   = os.path.exists( os.path.join(currentDirectory,".git") )
        if isMaven or isGit:
           self._createModule(currentDirectory[currentDirectory.rfind("/")+1:],currentDirectory,isMaven,isGit) 

        # Save each first-level subfolder as part of the repository
        for item in os.listdir(currentDirectory):
            subfolder = os.path.join(currentDirectory, item)
            if not os.path.isfile(subfolder):
               pomPath = os.path.join(currentDirectory, item,"pom.xml")
               gitPath = os.path.join(currentDirectory, item,".git")

               isMaven = os.path.exists(pomPath)
               isGit   = os.path.exists(gitPath)

               if isMaven or isGit:
                  self._createModule(item, subfolder, isMaven, isGit)

    def _createModule(self, folderName, subfolder, isMaven, isGit):
        record = {
            "name":folderName,
            "path":subfolder,
            "git": isGit,
            "maven": isMaven
        }
        self._databaseProject.insert(record)
        #Utils.printJSON(Utils.dictToJSON(record))

    def executeMacro(self, macro, repository=None):
        """
        \033[0;32mExecute a macro\033[0;0m

        \033[0;32mParameters:\033[0;36m
           macro (string): Key of the macro in the list to be executed

        \033[0;32mReturns:\033[0;36m
           string:Printing results
        \033[0;0m   
        """

        if not self._connectedDatabase:
           self._connectDBs()

        record = self._databaseMacro.search(where('key') == macro)
        if len(record) > 0:
           recordMacro = record[0]

           Console.title2("{c2}EXECUTING MACRO..: {c1}{key}{c2} - {desc}{cn}"\
                             .format(key=recordMacro["key"],desc=recordMacro["description"],\
                              c1=Colors.IGREEN,cn=Colors.RESET,c2=Colors.CYAN),True,False)
           
           tot   = len(recordMacro["executions"])
           index = 0
           for ex in recordMacro["executions"]:
               index += 1

               cmdArgs = self._prepareCommandArguments(ex["tool"], ex["command"])
               cmd     = cmdArgs["command"]
               args    = cmdArgs["arguments"]

               printArgs = "" 
               for i in args:
                   if " " in i.strip(): 
                      printArgs += ("\"" + i + "\"")
                   else:   
                      printArgs += i 

               Console.title("{c2}COMMAND..........: {c1}{cur}{c2} of {c1}{tot}{c2} --> {cmd}"\
                            .format(cur=index,tot=tot,cmd=Colors.ICYAN + ex["tool"] + Colors.CYAN + " " + cmd + " " + printArgs,\
                            c1=Colors.IGREEN,cn=Colors.RESET,c2=Colors.CYAN),True,False)                          
               print("")             

               pNames = ""
               # Selecting the Target Projects
               if len(ex["projects"]) == 0:
                  pNames = "ALL"
                  projects = self._databaseProject.all()
                  #self._databaseProject.search(where("name") == )
               else:
                  projects = []
                  for p in ex["projects"]:
                      if pNames != "": pNames += ", "
                      pNames += p
                      ProjectQ = Query()
                      r = self._databaseProject.search(ProjectQ.name == p)
                      if len(r) > 0:
                         projects.append(r[0])

               if len(projects) == 0:
                  Console.error("Projects [{}] for the macro {} was not found!" \
                                .format(Colors.IGREEN + pNames + Colors.RESET,Colors.IGREEN + macro + Colors.RESET)) 
                  return

               tool = ex["tool"]
               if tool == GIT:
                  pygit = PyGit(cmd,args,projects) 
                  pygit.execute()
                  
           Console.printFooter()       

           Console.printLine("Macro \"{}\" FINISHED!".format(Colors.IYELLOW +  macro + Colors.GREEN),False)
           print("")

        else:
           Console.error("Macro with the key {} was not found!".format(Colors.IGREEN + macro + Colors.RESET))


    def _prepareCommandArguments(self, tool, command):
        result  = {
            "command":command,
            "arguments":""
        }
        command = command.strip()
        if " " not in command:
           return result

        cmd  = command[:command.find(" ")].strip()
        args = command[command.find(" "):].strip()
        args = self._replaceArgsPlaceHolder(tool, command, args)

        result["command"]   = cmd
        result["arguments"] = args

        return result

    def _replaceArgsPlaceHolder(self, tool, originalCmd, args):
        userArguments = {}
        for idx, val in enumerate(sys.argv):
            if idx > 1:
               userArguments[idx-1] = val

        ARG_SEPARATOR = "{{#arg}}"
        isTherePlaceholders = False
        regexp = re.compile(r'\$[0-9]') # Search for $1 $2 $3 $4...
        if regexp.search(args):
           isTherePlaceholders = True

           for i in range(1,10):
               placeHolder = "$"+str(i)
               if placeHolder in args and i in userArguments:
                  args = args.replace(placeHolder,ARG_SEPARATOR + userArguments[i] + ARG_SEPARATOR) 

           if isTherePlaceholders:
              if regexp.search(args):
                 print("")
                 print("  " + Emoticons.error() + " " + Colors.GREEN + "The \033[1;91m{} {}\033[32m contains arguments not passed!".format(tool, originalCmd))
                 print("       Please, check it...")
                 print("")
                 Console.printFooter()
                 sys.exit() 

        argsArray = []
        if args.startswith(ARG_SEPARATOR):
           argsArray.append(args.replace(ARG_SEPARATOR,""))
        else:
           for a in args.split(ARG_SEPARATOR):
               argumentItemCleaned = a.replace(ARG_SEPARATOR,"")
               if len(argumentItemCleaned) > 1:
                  argsArray.append(argumentItemCleaned)
               
        return argsArray 
            
def main():
    pymvngit = PyMvnGit()
    if len(sys.argv) < 2:
       syntax()
       sys.exit()

    command = sys.argv[1]   
    if "help".upper() == command.upper() or "-h".upper() == command.upper():
       syntax()
    elif "listProjects".upper() == command.upper() or "lp".upper() == command.upper():
       pymvngit.listProjects()
    elif "editMacros".upper() == command.upper() or "editMacro".upper() == command.upper() or "emac".upper() == command.upper():
       pymvngit.editMacros()   
    elif "listMacros".upper() == command.upper() or "lm".upper() == command.upper():
       summary = True
       if len(sys.argv) > 2 and sys.argv[2] == "-v":
          summary = False
       pymvngit.listMacros(summary)
    elif "start".upper() == command.upper():
       pymvngit.start()
    elif "clone".upper() == command.upper():
       if len(sys.argv) < 6:
          Console.error("Missing parameters! Please, check the syntax of the command clone!")
          syntax(clearScreen=False)
          sys.exit()
       elif len(sys.argv) == 7:
          # Must have 6 or 8 parameters 
          Console.error("Missing parameters! Please, check the syntax of the command clone!")
          syntax(clearScreen=False)
          sys.exit() 
       else:
          repositories   = []
          localPath      = ""
          branchName     = "master" 
          index          = 0
          isRepoListFile = False
          for a in sys.argv:
              index += 1
              if a == "-r":
                 for repo in sys.argv[index].split(","):
                     repositories.append(repo.strip())
              elif a == "-p":
                 localPath = sys.argv[index].strip()
              elif a == "-f":
                 repositories.append(sys.argv[index].strip())
                 isRepoListFile = True
              elif a == "-b":
                 branchName = sys.argv[index].strip()   

          pymvngit.clone(repositories,localPath,branchName,isRepoListFile)       
    else:
       pymvngit.executeMacro(command)

def syntax(clearScreen=True):
    if clearScreen:
       Console.clear()
    Console.printHeaderCommand("PyGitMvn Tool")    
    print("""
        {green}Tool to manage a group of Git/Maven projects.

        {iblue}MACROS{green}
        ------
        A sequence of Git/Maven commands to run sequentially over project(s) of a repository.

        {iblue}REPOSITORY{green}
        ----------
        A collection of Git/Maven projects that can be managed together.

        {iblue}FUNCTIONS:{green}
        - start...........: {blue}Create a repository from the current directory. Every subfolder will be 
                            analyzed and if it's a Git/Maven project, will be part of this created repository.{green}
        - clone...........: {blue}Create a repository cloning all the URL repository(ies) passed as argument
                            {green}#{cyan}arguments:
                            - Repositories.......: {cyan}(1){green} -r "https://github/projectA, https://github/projectB"{green}
                                                      {cyan}or{green}
                                                   {cyan}(2){green} -f file-name.txt     {cyan}# file with the list of repositories
                            - Local path.........: {green}-p "/home/my/projects"{cyan}
                            - Branch (optional)..: {green}-b "develop"{cyan}             #"branch" is the default value
        - {cyan}[{green}macro{cyan}]{green}.........: {blue}Name of a macro to be executed.{green}
        - listProjects....: {blue}List the projects part of the repository associated with the current directory.{green}
        - listMacros......: {blue}List the macros configured. 
                            {green}#{cyan}arguments:
                            - Show more details, print a table for each one of them..: {green}{{-v}}{cyan}
        {iblue}SYNTAX:{green}
          pymvngit {iblue}[MACRO] {cyan}{{arguments}}
        {iblue}EXAMPLES:{green}
          pymvngit {iblue}build-all{green}
          pymvngit {iblue}add-push{cyan} -A Patch v0.5.7 BugFixCrashing{green}
          pymvngit {iblue}status-all{green}
          pymvngit {iblue}install-commons{green}
          pymvngit {iblue}ltags{green}

    """.format(igreen=Colors.IGREEN,iblue=Colors.IBLUE,ired=Colors.IRED,blue=Colors.BLUE, \
               green=Colors.GREEN,reset=Colors.RESET,cyan=Colors.CYAN,icyan=Colors.ICYAN))

if __name__ == '__main__':
    main()

    """
    {
        "key":"install_commons",
        "description": "Build and install enrollment client locally",
        "commands":[
            {
                "command":"maven",
                "arguments":["clean","install"],
                "projects":["teachstore-commons"]
            },
            {
                "command":"git",
                "arguments":"-a push -r commons -b develop -cm $1",
                "projects":["teachstore-commons"]
            }
        ]
    }
    """