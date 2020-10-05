import venv
import click
from pathlib import Path
import confuse
import sys
import subprocess
import deadsimplevenv.__init__
import logging
from alive_progress import alive_bar, config_handler
from jinja2 import Environment, FileSystemLoader
import random
import shutil
import github
import gitlab
import git
from urllib.parse import urlparse
import questionary

CONFIG = confuse.Configuration("deadsimplevenv", deadsimplevenv.__init__.__name__)


def validate_project_option(value):
    if value is not None:
        if Path(value).exists():
            removeit = questionary.confirm(
                f"Directory {value} exists, do you want to remove it?",
            ).ask()

            if not removeit:
                raise click.Abort()
            else:
                shutil.rmtree(Path(value))
    return value


@click.command()
@click.option(
    "-p",
    "--project",
    help="Project name",
    type=click.Path(exists=False),
)
@click.option(
    "-d",
    "--description",
    help="Brief project description",
    type=str,
)
@click.option(
    "-u",
    "--username",
    help="Your username",
    default=CONFIG["user"]["username"].get(None),
    type=str,
)
@click.option(
    "-n",
    "--name",
    help="Your full name",
    default=CONFIG["user"]["fullname"].get(None),
    type=str,
)
@click.option(
    "-e",
    "--email",
    help="Your email adress",
    default=CONFIG["user"]["email"].get(None),
    type=str,
)
@click.option(
    "-l",
    "--license",
    help="Project license",
    default=CONFIG["license"].get(None),
    type=click.Choice(["MIT", "GNU", "EMPTY"]),
    show_default=True,
)
@click.option(
    "--devops_platform",
    help="Your devops platform",
    default=CONFIG["devops"]["platform"].get(None),
    type=click.Choice(["github", "gitlab"]),
    show_default=True,
)
@click.option(
    "--devops_url",
    help="Your devops url",
    default=CONFIG["devops"]["url"].get(None),
    show_default=True,
)
@click.option(
    "--devops_group",
    help="Your devops group",
    default=CONFIG["devops"]["group"].get(None),
    show_default=True,
)
@click.option("--makerepo", is_flag=True, help="Create repo in DEVOPS", default=False)
@click.option(
    "--norepo", is_flag=True, help="Do not create repo in DEVOPS", default=False
)
@click.option(
    "--private/--public",
    default=CONFIG["devops"]["private_visibility"].get(True),
    help="Create repo in DEVOPS",
    show_default=True,
)
@click.option(
    "--token",
    default=CONFIG["devops"]["token"].get(None),
    help="DEVOPS token",
)
def cli(
    project,
    description,
    username,
    name,
    email,
    license,
    devops_platform,
    devops_url,
    devops_group,
    makerepo,
    norepo,
    private,
    token,
):
    """You can load custom config from ~/.config/deadsimplevenv"""

    project = (
        questionary.text("Tell me your smashing project name:")
        .skip_if(project is not None)
        .ask()
    )
    validate_project_option(project)
    project = Path(project)
    description = (
        questionary.text("One line brief description of your project:")
        .skip_if(description is not None)
        .ask()
    )
    username = questionary.text("Your username:").skip_if(username is not None).ask()
    name = (
        questionary.text("Your full name:", default=username)
        .skip_if(name is not None)
        .ask()
    )
    email = questionary.text("Your email address:").skip_if(email is not None).ask()
    license = (
        questionary.select(
            "Which license type you want to use:",
            choices=["MIT", "GNU", "EMPTY"],
            default="EMPTY",
        )
        .skip_if(license is not None)
        .ask()
    )

    devops_platform = (
        questionary.select(
            "Choose your devops platform:",
            choices=["github", "gitlab"],
            default="github",
        )
        .skip_if(devops_platform is not None)
        .ask()
    )
    devops_url = (
        questionary.autocomplete(
            "Give me your devops url:",
            choices=["https://github.com", "https://gitlab.com"],
            default="https://github.com",
        )
        .skip_if(devops_url is not None)
        .ask()
    )

    if not makerepo and not norepo:
        makerepo = questionary.confirm("Create repo in DEVOPS:").ask()
    elif norepo:
        makerepo = False
    if makerepo:
        token = (
            questionary.password("Your devops token:").skip_if(token is not None).ask()
        )

    logging.debug(f"Used config {CONFIG.config_dir()}")

    config_handler.set_global(
        bar="filling", unknown="waves2", spinner="waves2", length=10
    )

    if project.exists():
        raise FileExistsError

    if devops_group == "username":
        devops_group = username

    vardict = {
        "project": project.name,
        "description": description,
        "username": username,
        "name": name,
        "email": email,
        "license": license,
        "devops_platform": devops_platform,
        "devops_url": devops_url,
        "devops_group": devops_group,
    }

    pip_modules = CONFIG["pip_modules"].get(list)
    if makerepo:
        makerepotasks = 2
    else:
        makerepotasks = 0
    tasks = len(pip_modules) + makerepotasks + 2
    click.secho("\nMaking it virtual:", bold=True, fg="blue")
    with alive_bar(tasks, calibrate=10) as bar:
        bar.text(f"creating venv 👾")
        python_exe = create_venv_and_return_python_exe(project)
        bar()
        random_emoji = ["💾", "📀", "💿", "💽", "📡", "🛒", "🔨"]
        for module in pip_modules:
            bar.text(f"installing {module} {random.choice(random_emoji)}")
            install_pip_package(str(python_exe), module)
            bar()
        bar.text(f"Folder structur preparation 📁")
        make_project_structure(project, vardict)
        bar()
        url = None
        clone_url = None
        if makerepo:
            bar.text("Making devops project 💥")
            token = CONFIG["devops"]["token"].as_str()
            if devops_platform == "github":
                url, clone_url = github_create_repo(
                    token, project.name, description, private
                )
            elif devops_platform == "gitlab":
                url, clone_url = gitlab_create_repo(
                    devops_url, token, project.name, description, private
                )
            else:
                click.secho("Unsupported platform selected!")
            bar()
            bar.text(f"Pushing first commit 📩")
            if clone_url is not None:
                git_init(project, username, email, clone_url)
            bar()

    if url:
        click.secho(f"Project URL: {url} \n", bold=True)
    click.secho("Your environment is good to go 🎉\n", bold=True, fg="green")


def create_venv_and_return_python_exe(project: Path):
    venv_dir = project / ".venv"
    venv.create(venv_dir, with_pip=True)
    return venv_dir / "bin" / "python"


def git_init(project, username, email, url):
    repo_dir = project
    repo = git.Repo.init(repo_dir)
    repo.create_remote("origin", url)
    repo.config_writer().set_value("user", "name", username).release()
    repo.config_writer().set_value("user", "name", email).release()
    repo.git.add(all=True)
    repo.index.commit("initial commit")
    repo.git.push("origin", "master")


def rename(templates, file, vardict):
    env = Environment(loader=FileSystemLoader(templates))
    template = env.get_template(file)
    return template.render(vardict)


def github_create_repo(token, username, desc, private):
    g = github.Github(token)
    user = g.get_user()
    url = None
    clone_url = None
    try:
        repo = user.create_repo(username, desc, private=private)
    except github.GithubException as errmsg:
        print(f"WARNING: Unable to create repo in Github.")
        print(f"WARNING: {errmsg}\n")
    else:
        url = repo.html_url
        clone_url = repo.clone_url
        uri = urlparse(clone_url)
        clone_url = f"{uri.scheme}://{username}:{token}@{uri.netloc}{uri.path}"

    return url, clone_url


def gitlab_create_repo(url, token, full_name, desc, private):
    gl = gitlab.Gitlab(url, token)
    url = None
    clone_url = None
    visibility = "private" if private else "public"
    try:
        repo = gl.projects.create(
            {"name": full_name, "description": desc, "visibility": visibility}
        )
    except gitlab.exceptions.GitlabCreateError as errmsg:
        print("WARNING: Unable to create repo in Gitlab.")
        print(f"WARNING: {errmsg}\n")
    else:
        url = repo.web_url
        clone_url = repo.http_url_to_repo
        uri = urlparse(clone_url)
        clone_url = f"{uri.scheme}://oauth2:{token}@{uri.netloc}{uri.path}"

    return url, clone_url


def make_project_structure(project, vardict):
    script_folder = Path(__file__).parents[1].absolute()
    data_folder = script_folder / "data"
    template_dir = data_folder / "static"
    templates = [
        template for template in template_dir.glob("**/*") if template.is_file()
    ]
    for template in templates:
        renamed = rename(template_dir, template.name, vardict)
        with open(project / template.name, "w") as target:
            target.write(renamed)
    project_dir = project / project.name
    project_dir.mkdir()
    project_dir.joinpath("__ini__.py").touch()
    license_f = vardict["license"]
    source_license_file = data_folder / "license" / f"LICENSE_{license_f}"
    target_file = project / "LICENSE"
    shutil.copy(source_license_file, target_file)


def install_pip_package(python_exec, package):
    subprocess.check_call(
        [python_exec, "-m", "pip", "install", "--upgrade", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def main():
    click.secho("\n💀💀💀 deadsimplevenv", bold=True, fg="green")
    click.secho(
        "Let's go create your snaky 🐍 workspace together.\n",
        bold=True,
    )
    # pylint: disable=no-value-for-parameter
    cli()


if __name__ == "__main__":
    main()
