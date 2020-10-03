
import ast
import configparser
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import git
from git import RemoteProgress

from pymvngit.console import Console
from pymvngit.utils import Colors, Emoticons, Utils


class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, msg=''):
        if msg:
            if Emoticons.isWindows():
               sys.stdout.write("\r  " + Colors.BLUE + " --> " + Colors.GREEN + msg + Colors.RESET)
            else:   
               sys.stdout.write("\r  " + Colors.BLUE + " --> " + Colors.GREEN + msg + Colors.RESET)


class PullProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, msg=''):
        if msg:
           if Emoticons.isWindows():
               sys.stdout.write("\r  " + Colors.BLUE + " --> " + Colors.GREEN + msg + Colors.RESET)
           else:   
               sys.stdout.write("\r  " + Colors.BLUE + " --> " + Colors.GREEN + msg + Colors.RESET)

LABEL_LENGTH = 100

class PyGit:

    def __init__(self, command, arguments, projects):
        self._projects  = projects
        self._command   = command
        self._arguments = arguments
        self._executed  = False
        self.response   = None
        
    def execute(self):
        self._executed = True
        if "add" == self._command:
            self._add()
        elif "commit" == self._command:
            self._commit()    
        elif "status" == self._command:
            self._status()
        elif "push" == self._command:
            self._push()
        elif "pull" == self._command:
            self._pull()
        elif "tag" == self._command:
            self._tag()
        elif "clone" == self._command:
            self._clone()
        # custom command    
        elif "listTags".upper() == self._command.upper() or "listTag".upper() == self._command.upper():
            self._listTags()     
        else:
            Console.error("Git Command {} does not exist!".format(Colors.BIRED +  self._command + Colors.RESET))
            self._executed = False

    def _add(self):
        addAll = False
        if len(self._arguments) == 1 and self._arguments[0] == "-A":
           # -A to add all files 
           addAll = True
        else:
           # specific files to add 
           args = " ".join(self._arguments)
        msg  = ""
        for p in self._projects:
            added = False
            repo = git.Repo(p["path"])
            currentBranch = repo.active_branch
            current       = repo.create_head(currentBranch)
            current.checkout()
            if repo.index.diff(None) or repo.untracked_files:
               added = True
               origin = repo.remotes.origin
               
               msg  = Colors.BLUE + "Added " + Colors.GREEN + "project {}".format(Colors.IBLUE +p["name"] + Colors.GREEN) 
               isOK = True
               try:
                   if addAll:
                      repo.git.add(A=True)
                   else:   
                      repo.git.add(args)
               except git.exc.GitCommandError as e:
                   isOK = False
                   msg += "\n  " + Colors.IRED + Emoticons.error() + " ERROR! \n  " + str(e)
               except:
                   isOK = False
                   msg += Colors.IRED + " Ops... " + Colors.IRED + str(sys.exc_info()[0]) 
                   msg = Console.addKoMsg(LABEL_LENGTH,msg)    
               if isOK:    
                   msg = Console.addOkMsg(LABEL_LENGTH,msg)    
               Console.printLine(msg)

            if not added:
               m = "Nothing to add for {repo}".\
                   format(repo=Colors.IBLUE +p["name"] + Colors.GREEN,iblue=Colors.IBLUE,green=Colors.GREEN)
               Console.printLine(Console.addOkMsg(LABEL_LENGTH,m))
               del m

    def _clone(self):
        if len(self._arguments) < 1:
           Console.error("The arguments \"{}\" doesn't seem to be a repository, or a list of them, to be cloned! Please, review it." \
           .format(Colors.IBLUE + " ".join(self._arguments) + Colors.GREEN))
           sys.exit()

        clonedRepos    = []
        repositories   = self._arguments[0]
        localPath      = self._arguments[1]
        branchName     = self._arguments[2]
        isRepoListFile = self._arguments[3]

        if not os.path.exists(localPath):
           Console.line(Emoticons.pin() +  Colors.GREEN + " Local path {} does not exist, creating..." \
                        .format(Colors.IBLUE+localPath+Colors.GREEN),False, False)
           os.makedirs(localPath)

        if isRepoListFile:
           fileName =  repositories[0]
           if not os.path.exists:
               Console.error("The file {} was not found!".format(Colors.IBLUE + fileName + Colors.GREEN))
               sys.exit()
               
           repositories = []    
           with open(fileName,'r') as f:
               for l in f:    
                   repositories.append(l.replace("\n","").strip())

        totalRepo = len(repositories)
        Console.printHeaderCommand("Clone Repositories, Total {}".format(Colors.IBLUE+str(totalRepo)+Colors.GREEN))   

        idx = 0
        for git_repo in repositories:
            idx += 1
            nameRepo        =  git_repo[git_repo.rfind("/")+1:].replace(".git","")
            localFolderName =  os.path.join(localPath,nameRepo)
            
            doIt         = True
            accessDenied = False
            isMaven      = False
            if os.path.exists(localFolderName):
               resp = input(Colors.GREEN + "{green}The folder {iblue}{folder}{green} already exists, delete and clone? [{igreen}Y{green}/{igreen}N{green}] ".\
                            format(igreen=Colors.IGREEN,green=Colors.GREEN,iblue=Colors.IBLUE,blue=Colors.BLUE,folder=localFolderName))
               if resp.strip().upper() == "Y":
                  try: 
                    shutil.rmtree(localFolderName)
                    doIt = True
                  except PermissionError as e:
                    msg = "Access Denied! Please remove the folder {} manually".format(Colors.IBLUE + localFolderName + Colors.GREEN)
                    print(Emoticons.error(),msg)
                    doIt = False
                    accessDenied = True
               else:
                  doIt = False 
                  
            if doIt:                  
               Console.line(Colors.GREEN + "Cloning repository" + " [{iblue}{idx:02d}{green} of {iblue}{total:02d}{green}] --> {iblue}{git_repo}{green}". \
                   format(idx=idx,iblue=Colors.IBLUE,git_repo=git_repo,green=Colors.GREEN,total=totalRepo),False,False)
               git.Repo.clone_from(git_repo, localFolderName, branch=branchName, progress=CloneProgress())           
               print(Colors.GREEN)                   

               for path in Path(localFolderName).rglob('pom.xml'):
                   isMaven = True
                   break

               clonedRepos.append({"name":nameRepo,"path":localFolderName,"git":"true","maven":isMaven})
            else:
               if not accessDenied:
                  Console.line(Colors.GREEN + "Not cloned!       " + " [{iblue}{idx:02d}{green} of {iblue}{total:02d}{green}] --> {iblue}{git_repo}{green} The folder Already exists!". \
                               format(idx=idx,iblue=Colors.IBLUE,git_repo=git_repo,green=Colors.GREEN,total=totalRepo),False,False)     

        Console.printFooter()
        if len(clonedRepos) > 0:  
           self.response = clonedRepos

    def _commit(self):
        if self._arguments[0].strip().lower() == "-m" and len(self._arguments) > 1:
           messageCommit = self._arguments[1] 
        else:
           Console.error("The arguments \"{}\" for git commit seems to be invalid, please check it!" \
           .format(Colors.IBLUE + " ".join(self._arguments) + Colors.GREEN))
           sys.exit()
        msg  = ""
        for p in self._projects:
            commited = False
            repo = git.Repo(p["path"])
            currentBranch = repo.active_branch
            current       = repo.create_head(currentBranch)
            current.checkout()
            if repo.index.diff("HEAD"):
               commited = True
               origin = repo.remotes.origin
               
               msg  = Colors.BLUE + "Commited " + Colors.GREEN + "project {}".format(Colors.IBLUE +p["name"] + Colors.GREEN)
               isOK = True
               try:
                   repo.git.commit(m=messageCommit)
               except git.exc.GitCommandError as e:
                   isOK = False
                   msg += "\n  " + Colors.IRED + Emoticons.error() + " ERROR! \n  " + str(e)
               except:
                   isOK = False
                   msg += Colors.IRED + " Ops... " + Colors.IRED + str(sys.exc_info()[0]) 
                   msg = Console.addKoMsg(LABEL_LENGTH,msg)    
               if isOK:    
                   msg = Console.addOkMsg(LABEL_LENGTH,msg)    
               Console.printLine(msg)
   
            if not commited:
               m = "Nothing to commit for {repo}".\
                   format(repo=Colors.IBLUE +p["name"] + Colors.GREEN,iblue=Colors.IBLUE,green=Colors.GREEN)
               Console.printLine(Console.addOkMsg(LABEL_LENGTH,m))
               del m    

    def _status(self):
        msg = ""
        magnifier = "<< "  + Emoticons.magnifier()
        ok        = "Ok!"  + Emoticons.ok()
        for p in self._projects:
            nothingToCommit = True
            msg = Colors.BLUE + "Checking Status " + Colors.GREEN + "project {}".format(Colors.IBLUE +p["name"] + Colors.GREEN)
            msg = Console.addToMsg(LABEL_LENGTH,msg,magnifier)

            repo  = git.Repo(p["path"])
            items = repo.index.diff(None)
            
            if len(items) > 0:
                nothingToCommit = False
                msg += "\n    " + Emoticons.pointRight() + Colors.GREEN + " Changed files:"
                idx_chg_files = 0
                for item in items:
                    idx_chg_files  += 1
                    msg += "\n       " + Colors.GREEN + "{:02d} ".format(idx_chg_files) + Colors.WHITE + ">>" + Colors.RESET + " " + item.a_path   
            files = repo.untracked_files
            if len(files) > 0:
                nothingToCommit = False
                msg += "\n    " + Emoticons.pointRight() + Colors.GREEN + " New added files:"
                idx_new_files = 0
                for file in files:
                    idx_new_files  += 1
                    msg += "\n       " + Colors.GREEN + "{:02d} ".format(idx_new_files) + Colors.WHITE + ">>" + Colors.RESET + " " + file

            if nothingToCommit:
               msg = msg.replace(magnifier,ok) 
               #msg = Console.addOkMsg(LABEL_LENGTH,msg)    
                
            Console.printLine(msg)

    def _push(self):
        msg = ""
        for p in self._projects:
            pushed = False
            repo = git.Repo(p["path"])
            currentBranch = repo.active_branch
            current       = repo.create_head(currentBranch)
            current.checkout()
            
            pushed = True
            origin = repo.remotes.origin
            
            pushingMsg = "{blue}Pushing {green}repository {iblue}{repo}{reset} {green}to branch origin/{branch}" \
                         .format(repo=p["name"],branch=currentBranch,iblue=Colors.IBLUE,green=Colors.GREEN,reset=Colors.RESET,blue=Colors.BLUE)
            pushingMsg = Console.addWaitMsg(LABEL_LENGTH,pushingMsg)
            Console.printLine(pushingMsg) 

            msg  = Colors.BLUE + "Pushed " + Colors.GREEN + "repository {} to branch origin/{}".format(Colors.IBLUE +p["name"] + Colors.GREEN,currentBranch) 
            isOK = True
            try:
                repo.git.push('--set-upstream', 'origin', current)
            except git.exc.GitCommandError as e:
                isOK = False
                msg += "\n  " + Colors.IRED + Emoticons.error() + " ERROR! \n  " + str(e)    
            except:
                isOK = False
                msg += Colors.RED + " Ops... " + Colors.IRED + str(sys.exc_info()[0]) 
                msg = Console.addKoMsg(LABEL_LENGTH,msg)    
            if isOK:    
                msg = Console.addOkMsg(LABEL_LENGTH,msg)
            Console.printLine(msg)

            if not pushed:
               print( Colors.GREEN + "  {iblue}--->{green} Ok! Nothing to push for {repo}".\
                      format(repo=Colors.IBLUE +p["name"] + Colors.GREEN,iblue=Colors.IBLUE,green=Colors.GREEN))
               

    def _pull(self):
        
        for p in self._projects:
            repo   = git.Repo(p["path"])
            origin = repo.remotes.origin
            msg  = Colors.BLUE + "Pulling " + Colors.GREEN + "repository \033[94m{}\033[32m from {}...". \
                   format(Colors.IBLUE + p["name"] + Colors.GREEN,origin.url)
            isOK = True
            try:
                origin.pull(progress=PullProgress())
            except git.exc.GitCommandError as e:
                isOK = False
                msg += "\n  " + Colors.IRED + Emoticons.error() + " ERROR! \n  " + str(e)     
            except:
                isOK = False
                msg += Colors.RED + " Ops... " + Colors.IRED + str(sys.exc_info()[0]) 
                msg = Console.addKoMsg(130,msg)    
            if isOK:    
               msg = Console.addOkMsg(130,msg)    
            Console.printLine(msg)    

    def _listTags(self):
        for p in self._projects:
            msg  = ""
            repo = git.Repo(p["path"])
            msg += Colors.BLUE + "Tags " + Colors.GREEN + "repository {}".format(Colors.IBLUE + p["name"] + Colors.RESET)
            for t in repo.tags:
                commitDate = time.strftime("%Y-%m-%d %H:%M %a", time.gmtime(t.commit.committed_date))
                tag        = Utils.alignRight(22,str(t))
                tagMsg     = t.tag.message
                tagCommit  = str(t.commit)
                msg += "\n       {green}>>{iblue} {tag} {blue}--> {green}{tagMsg}{reset},{green} {commitDate}{reset},{green} {tagCommit}" \
                    .format(green=Colors.GREEN,iblue=Colors.IBLUE,blue=Colors.BLUE,reset=Colors.RESET,tag=tag,tagMsg=tagMsg,commitDate=commitDate,tagCommit=tagCommit)
            Console.printLine(msg)


    def _tag(self):
        tag     = None
        message = None
        if self._arguments[0].strip().lower() == "-a" and len(self._arguments) > 1:
           # Annotated tag 
           tag = self._arguments[1] 
           if len(self._arguments) > 3 and self._arguments[2].strip().lower() == "-m":
              # Message for annoted tag 
              message = self._arguments[3]
           else:
              Console.error("The arguments \"{}\" for git tag seems to be invalid, please check it!" \
              .format(Colors.IBLUE + " ".join(self._arguments) + Colors.GREEN))
              sys.exit() 
        else:    
           # Not annoted tag, it is a simple tagging
           tag = self._arguments[0] 

        msg  = ""
        for p in self._projects:
            msgTagging = "  {iblue}---> Tagging{green} repository {iblue}{repo}{green} with tag {iblue}{tag}{green}". \
                        format(repo=p["name"],tag=tag,iblue=Colors.IBLUE,green=Colors.GREEN)
            print(msgTagging)  

            msg  = Colors.BLUE + "Tagged " + Colors.GREEN + "repository {iblue}{repo}{green} with tag {iblue}{tag}{green}". \
                        format(repo=p["name"],tag=tag,iblue=Colors.IBLUE,green=Colors.GREEN)
            isOK = True
            try:
                repo = git.Repo(p["path"])
                if message: 
                   new_tag = repo.create_tag(tag, message=message)
                else:
                   new_tag = repo.create_tag(tag) 
                repo.remotes.origin.push(new_tag)
            except git.exc.GitCommandError as e:
                isOK = False
                msg += "\n  " + Colors.IRED + Emoticons.error() + " ERROR! \n  " + str(e)    
            except:
                isOK = False
                msg += Colors.RED + " Ops... " + Colors.IRED + str(sys.exc_info()[0]) 
                msg = Console.addKoMsg(LABEL_LENGTH,msg)    
            if isOK:
               msg = Console.addOkMsg(LABEL_LENGTH,msg)
            Console.printLine(msg)

