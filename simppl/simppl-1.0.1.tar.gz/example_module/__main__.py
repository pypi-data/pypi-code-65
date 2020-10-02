import sys
from simppl.cli import CommandLineInterface

if __name__ == '__main__':
    ascii_logo = '''
                                                                                                                
          ____                       ___                         ,--,                                           
        ,'  , `.                   ,--.'|_                     ,--.'|             ,---,                         
     ,-+-,.' _ |                   |  | :,'   ,---.     ,---.  |  | :           ,---.'|      ,---.              
  ,-+-. ;   , ||                   :  : ' :  '   ,'\   '   ,'\ :  : '           |   | :     '   ,'\ ,--,  ,--,  
 ,--.'|'   |  ||    .--,         .;__,'  /  /   /   | /   /   ||  ' |           :   : :    /   /   ||'. \/ .`|  
|   |  ,', |  |,  /_ ./|         |  |   |  .   ; ,. :.   ; ,. :'  | |           :     |,-..   ; ,. :'  \/  / ;  
|   | /  | |--', ' , ' :         :__,'| :  '   | |: :'   | |: :|  | :           |   : '  |'   | |: : \  \.' /   
|   : |  | ,  /___/ \: |           '  : |__'   | .; :'   | .; :'  : |__         |   |  / :'   | .; :  \  ;  ;   
|   : |  |/    .  \  ' |           |  | '.'|   :    ||   :    ||  | '.'|        '   : |: ||   :    | / \  \  \  
|   | |`-'      \  ;   :           ;  :    ;\   \  /  \   \  / ;  :    ;        |   | '/ : \   \  /./__;   ;  \ 
|   ;/           \  \  ;           |  ,   /  `----'    `----'  |  ,   /         |   :    |  `----' |   :/\  \ ; 
'---'             :  \  \           ---`-'                      ---`-'          /    \  /          `---'  `--`  
                   \  ' ;                                                       `-'----'                        
                    `--`                                                                                       
    '''
    cli = CommandLineInterface(__file__, ascii_logo)
    cli.run(sys.argv)
