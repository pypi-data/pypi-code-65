import click
import requests
import json
import wget
import subprocess
import os
import webbrowser
import sys
import time
import platform 


@click.command()
@click.option('--url', default=None, help='Put the raw url of the script to be executed. Example: https://raw.githubusercontent.com/GDGVIT/HandWriter/master/install.sh')
@click.option('--path', default=None, help='Path of the script in localfile system to be executed. Example: /home/user/script.sh')
@click.option('--name', default=None, help='Name of the script in our cli to execute. Example: hello or hello.sh or hello.py')

def main_operation(name, path, url):
    """ In case something fucks up and process becomes zombie, run docker rm -f sandbox"""
    m = [bool(name), bool(path), bool(url)]
    if m.count(True) == 0:
        click.echo("No parameter selected, please use flag --help in case you need help or specify any one of the three flags, --url, --path, --name")
    elif m.count(True) > 1:
        click.echo("Please choose only one parameter")

    ## If name is chosen
    if name:
        output = requests.get('https://intelli-script.herokuapp.com/search/script/byName/?name={}'.format(name))
        new_output = json.loads(output.text)
        for i in range(len(new_output)):
            click.echo('{}) {}'.format(i+1, new_output[i]['name']))

        click.echo('\n')
        click.echo('Input the name of the script you want to select')
        choice = input('Enter choice: ')

        extension = choice.split('.')[-1]
        if len(choice.split('.')) <= 1:
            sys.exit('Need a valid extension for the file! ')
        if extension == 'py':
            extension_type = 'python'
        elif extension == 'sh':
            extension_type = 'shell'
        else:
            name = name + '.sh'
            extension_type = 'shell'

        
        click.echo('Select 1 if you just want to execute the script, 2 if you want to download it, or 3 to view it.')
        new_choice = int(input('Enter choice now: '))
        if new_choice == 1:
            for j in new_output:
                if j['name'] == choice:
                    click.echo("========{}=======".format(choice))
                    try:
                        os.remove(choice)
                    except Exception:
                        pass
                    print(j['url'])
                    file = wget.download(j['url'])
                    click.echo("\n")
                    
                    if platform.system() == 'Windows':
                        subprocess.run(shlex.split("""for /f "tokens=5" %a in ('netstat -aon ^| find ":8080" ^| find "LISTENING"') do taskkill /f /pid %a"""))
                    elif platform.system() == 'Linux':
                        subprocess.run(['fuser', '-k', '10000/tcp'])

                    subprocess.run(['docker', 'rm','-f', 'sandbox'])


                    if extension_type == 'shell':
                        proc = subprocess.Popen(['timeout', '-s', '3', '10m', 'gotty','-w','-p', '10000', 'docker', 'run', '-it','-m', '50M', '--name', 'sandbox', '--rm', '-v', '{}/{}:/{}:ro'.format(os.getcwd(),choice,choice), 'bash:4.4'])
                    else:
                        proc = subprocess.Popen(['timeout', '-s', '3', '10m', 'gotty','-w','-p', '10000', 'docker', 'run', '-it','-m', '50M', '--name', 'sandbox', '--rm', '-v', '{}/{}:/{}:ro'.format(os.getcwd(),choice,choice), 'python:3.8-slim-buster', 'bash'])
                    try:
                        webbrowser.open("http://127.0.0.1:10000/")
                        while True:
                            if proc.poll() == None:
                                pass
                            else:
                                print('Please wait while the process is being gracefully terminated by the script.........')
                                break
                    finally:
                        proc.terminate()
                        try:
                            outs, _ = proc.communicate(timeout=3)
                        except subprocess.TimeoutExpired:
                            print('Script did not end normally, forceful measure by sript !!..... ')
                        os.remove(choice)
                        subprocess.run(['docker', 'rm', '-f', 'sandbox'])
                        click.echo("======== end =======")
        elif new_choice == 2:
            for j in new_output:
                if j['name'] == choice:
                    click.echo("========Downloading {}=======".format(i))
                    file = wget.download(j['url'])
                    click.echo("\n")
        
        elif new_choice == 3:
            for j in new_output:
                if j['name'] == choice:
                    click.echo("========Showing {}=======".format(i))
                    file = requests.get(url=j['url'])
                    click.echo("\n")
                    click.echo(file.text)
                    click.echo("\n")
                    click.echo("======== end =======")
    
        else:
            click.echo("Invalid option entered!")

    if path:
        click.echo('Enter the file name with extension')
        name = input('Enter name: ')

        extension = name.split('.')[-1]
        if len(name.split('.')) <= 1:
            sys.exit('Need a valid extension for the file! ')
        if extension == 'py':
            extension_type = 'python'
        elif extension == 'sh':
            extension_type = 'shell'
        else:
            name = name + '.sh'
            extension_type = 'shell'
        
        click.echo('Select 1 if you just want to execute the script, or 2 to view it.')
        new_choice = int(input('Enter choice now: '))
        if new_choice == 1:
            click.echo("\n")
            
            if platform.system() == 'Windows':
                subprocess.run(shlex.split("""for /f "tokens=5" %a in ('netstat -aon ^| find ":8080" ^| find "LISTENING"') do taskkill /f /pid %a"""))
            elif platform.system() == 'Linux':
                subprocess.run(['fuser', '-k', '10000/tcp'])
            
            subprocess.run(['docker', 'rm','-f', 'sandbox'])
            if extension_type == 'shell':
                proc = subprocess.Popen(['timeout', '-s', '3', '10m', 'gotty','-w','-p', '10000', 'docker', 'run', '-it','-m', '50M', '--name', 'sandbox', '--rm', '-v', '{}:/{}:ro'.format(path, name), 'bash:4.4'])
            else:
                proc = subprocess.Popen(['timeout', '-s', '3', '10m', 'gotty','-w','-p', '10000', 'docker', 'run', '-it','-m', '50M', '--name', 'sandbox', '--rm', '-v', '{}:/{}:ro'.format(path, name), 'python:3.8-slim-buster', 'bash'])
            
            try:
                webbrowser.open("http://127.0.0.1:10000/")
                while True:
                    if proc.poll() == None:
                        pass
                    else:
                        print('Please wait while the process is being gracefully terminated by the script.........')
                        break
            finally:
                proc.terminate()
                try:
                    outs, _ = proc.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    print('Script did not end normally, forceful measure by sript(Need to figure this out) !!..... ')
                subprocess.run(['docker', 'rm', '-f', 'sandbox'])
                click.echo("======== end =======")
        
        elif new_choice == 2:
            click.echo("========Showing {}=======".format(name))
            with open(path, 'r') as newfile:
                file = newfile.read()
            click.echo("\n")
            click.echo(file)
            click.echo("\n")
            click.echo("======== end =======")
    
        else:
            click.echo("Invalid option entered!")

    if url:
        print(url)
        click.echo('Enter the file name with extension')
        name = input('Enter name: ')


        extension = name.split('.')[-1]
        if len(name.split('.')) <= 1:
            sys.exit('Need a valid extension for the file! ')
        if extension == 'py':
            extension_type = 'python'
        elif extension == 'sh':
            extension_type = 'shell'
        else:
            name = name + '.sh'
            extension_type = 'shell'
                
        click.echo('Select 1 if you just want to execute the script, 2 if you want to download it, or 3 to view it.')
        new_choice = int(input('Enter choice now: '))
        if new_choice == 1:
            file = wget.download(url)
            click.echo("\n")
            if platform.system() == 'Windows':
                subprocess.run(shlex.split("""for /f "tokens=5" %a in ('netstat -aon ^| find ":10000" ^| find "LISTENING"') do taskkill /f /pid %a"""))
            elif platform.system() == 'Linux':
                subprocess.run(['fuser', '-k', '10000/tcp'])
            
            subprocess.run(['docker', 'rm','-f', 'sandbox'])
            
            
            if extension_type == 'shell':
                proc = subprocess.Popen(['timeout', '-s', '9', '10', 'gotty','-w','-p', '10000', 'docker', 'run', '-it','-m', '50M', '--name', 'sandbox', '--rm', '-v', '{}/{}:/{}:ro'.format(os.getcwd(),name,name), 'bash:4.4'])
            else:
                proc = subprocess.Popen(['timeout', '-s', '9', '10m', 'gotty','-w','-p', '10000', 'docker', 'run', '-it','-m', '50M', '--name', 'sandbox', '--rm', '-v', '{}/{}:/{}:ro'.format(os.getcwd(),name,name), 'python:3.8-slim-buster', 'bash'])
            
            
            try:
                webbrowser.open("http://127.0.0.1:10000/")
                while True:
                    if proc.poll() == None:
                        pass
                    else:
                        print('Please wait while the process is being gracefully terminated by the script.........')
                        break
            finally:
                proc.terminate()
                try:
                    outs, _ = proc.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    print('Script did not end normally, forceful measure by sript !!..... ')
                os.remove(name)
                subprocess.run(['docker', 'rm', '-f', 'sandbox'])
                click.echo("======== end =======")

        elif new_choice == 2:
            click.echo("========Downloading {}=======".format(name))
            file = wget.download(url)
            click.echo("\n")
        
        elif new_choice == 3:
            click.echo("========Showing {}=======".format(name))
            file = requests.get(url=url)
            click.echo("\n")
            click.echo(file.text)
            click.echo("\n")
            click.echo("======== end =======")
    
        else:
            click.echo("Invalid option entered!")


                         
if __name__ == '__main__':
    main_operation()