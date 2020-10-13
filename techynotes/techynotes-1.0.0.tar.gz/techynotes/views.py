from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
import base64
import json
import shutil
import sys
from django.views.decorators.csrf import csrf_exempt
from git import Repo
from github import Github
from github import InputGitTreeElement
from datetime import date

# Create your views here.
today = date.today()

def home(request):
    username=os.getenv("GITUNAME")
    if username is None:
        username = ""
    return render(request, 'homepage.html', {"username":username})


def loadnote(request):
    filename = request.GET.get('filename')
    file_path = os.path.join(os.path.abspath("."),"mainscreen","mynotes",filename)
    with open(file_path,"r") as f:
        file_data = f.readlines()
    return HttpResponse(file_data)

def search_user(request):
    username = request.GET.get('username')
    url = "https://github.com/"+username
    status = ""
    try:
        check_user = requests.get(url)
        if(check_user.status_code == 200):
            status = "userexists"
        else:
            status = "usernotexists"
    except:
        status = "usernotexists"
    if(status == "userexists"):
        return HttpResponse("success")
    else:
        return HttpResponse("fail")

def save_file(request):
    filename = request.GET.get("filename")
    filename = filename+".html"
    file_data = request.GET.get("finalbody")
    path = os.path.join(os.path.abspath("."),"mainscreen","mynotes",filename)    
    try:
        with open(path, "w") as f:
            f.write(file_data)
    except Exception as e:
        print(str(e))
        return HttpResponse("fail")
    else:
        push_to_git("")
        return HttpResponse("success")

def push_to_git(request):
    user = os.getenv("GITUNAME")
    password = os.getenv("GITPASS")
    g = Github(user,password)
    repo = g.get_user().get_repo('_techynotes')
    html_list = []
    file_names = []
    source = os.path.join(os.path.abspath("."),"mainscreen","mynotes")
    file_list = list(os.listdir(source))
    for file in file_list:
        if file.endswith(".html"):
            html_list.append(os.path.join(os.path.abspath("."),"mainscreen","mynotes",file))
            file_names.append(file)
    commit_message = 'created on '+today.strftime("%d/%m/%Y")
    master_ref = repo.get_git_ref('heads/master')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    element_list = list()
    for i, entry in enumerate(html_list):
        with open(entry) as input_file:
            data = input_file.read()
        if entry.endswith('.png'):
            data = base64.b64encode(data)
        element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
        element_list.append(element)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)

def fetch_user_notes(request):
    GHUSER = request.GET.get('username')
    fetch = ""
    destination = os.path.join(os.path.abspath("."),"mainscreen","mynotes")
    if not os.path.exists(destination):
        os.makedirs(destination)
    try:
        repodata = requests.get(
            "https://api.github.com/users/"+GHUSER+"/repos")
        response_code = repodata.status_code
        if (response_code == 200):
            repojson_list = repodata.json()
            num_of_repos = len(repojson_list)
            repositories = []
            for i in range(0, num_of_repos):
                repositories.append(repojson_list[i]["name"])
            if "_techynotes" in repositories:
                repo_url = "https://github.com/"+GHUSER+"/_techynotes.git"
                temp_dir = os.path.join(os.getcwd(), "tempdir/_techynotes")
                if (os.path.exists(temp_dir)):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                branch = "master"
                Repo.clone_from(repo_url, temp_dir, branch=branch)
                source = temp_dir
                if os.path.exists:
                    shutil.rmtree(destination)
                shutil.move(source, destination)
                fetch = "success"
        elif (response_code == 403):
            fetch = "service_unavailable"
    except Exception as e:
        print(e)
        fetch = "fail"
    notes = os.listdir(destination)
    html_notes = []
    for each in notes:
        if each.endswith(".html"):
            html_notes.append(each.split(".")[0])
    if(fetch == "success"):
        response = {"status": "success", "repo_list": html_notes}
        return HttpResponse(json.dumps(response), content_type="application/json")
    elif(fetch == "service_unavailable"):
        response = {"status": "service_unavailable"}
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        response = {"status": "fail"}
        return HttpResponse(json.dumps(response), content_type="application/json")

def login(request):
    try:
        os.environ['GITUNAME'] = request.POST.get("username")
        os.environ['GITPASS'] = request.POST.get("password")
    except:
        return HttpResponse("fail")
    else:
        response={"status":"success","username":os.getenv('GITUNAME')}
        return JsonResponse(response)

def logout(request):
    try:
        os.environ['GITUNAME'] = ""
        os.environ['GITPASS'] = ""
    except:
        return HttpResponse("fail")
    else:
        return HttpResponse("success")

