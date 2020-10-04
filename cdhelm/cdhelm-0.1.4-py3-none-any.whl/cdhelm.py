#!/usr/bin/env python
import yaml
import subprocess
import os
import stat
from collections import Mapping
from cdk8s import Include, Chart
from constructs import Construct


class HelmChart(Chart):
    def __init__(
        self, scope: Construct, ns: str, source_file: str, **kwargs,  # our app instance
    ):  # careful! this is not the K8s namespace but just a prefix for our resources
        super().__init__(scope, ns, **kwargs)
        self.manifest = Include(self, "dashboard", url=source_file)


class Helm:
    def __str__(self):
        return ""

    def __init__(self, repo, chart, name, version, path=".charts", namespace="default"):
        self.repo = repo
        self.chart = chart
        self.version = version
        self.path = path
        self.chart_path = (
            self.path + "/" + self.chart + "-" + self.version + "/" + self.chart
        )
        self.values_path = self.chart_path + "/rendered-values.yaml"

        self.values = {}
        self.new_values = {}
        self.name = name
        self.namespace = namespace

        # Pull chart
        self.__pull()

    def __pull(self):
        # Build the command with optional args
        cmd_pull = [
            "helm",
            "pull",
            "--repo",
            self.repo,
            "--destination",
            self.path,
            "--untardir",
            self.chart + "-" + self.version,
            "--version",
            self.version,
            "--untar",
            self.chart,
        ]

        # mkdir base dir just in case
        try:
            os.mkdir(self.path)
        except FileExistsError:
            {}
        # Don't bother if it already exists
        if not os.path.isdir(self.chart_path):
            # cd
            # pwd = os.getcwd()
            # try:
            # os.chdir(path)
            # except OSError:
            # print("Error: " + os.getcwd() + "/" + path + " Doesn't exist.")
            # exit(1)

            print(" ".join(cmd_pull))

            pull = subprocess.Popen(
                cmd_pull,
                # stdin =subprocess.PIPE,
                stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0,
            )
            pull.wait()

            # cd -
            # os.chdir(pwd)

        # grab values regardless
        self.__grab_values()

    def __grab_values(self):
        with open(self.chart_path + "/values.yaml") as f:
            value_yaml = f.read()
            self.values = yaml.load(value_yaml, Loader=yaml.FullLoader)

    def __update(self, orig_dict, new_dict):
        for key, val in new_dict.items():
            if isinstance(val, Mapping):
                tmp = self.__update(orig_dict.get(key, {}), val)
                orig_dict[key] = tmp
            elif isinstance(val, list):
                orig_dict[key] = orig_dict.get(key, []) + val
            else:
                orig_dict[key] = new_dict[key]
        return orig_dict

    def update(self, new_values):
        self.new_values = self.__update(self.new_values, new_values)
        self.values = self.__update(self.values, self.new_values)

    def updateFile(self, filename):
        with open(filename) as f:
            value_yaml = f.read()
            new_values = yaml.load(value_yaml, Loader=yaml.FullLoader)
            self.update(new_values)

    def render(self, path):
        self.values_path = path
        with open(path, "w") as f:
            yaml.dump(self.new_values, f)

        cmd = [
            "helm",
            "template",
            "--values",
            path,
            "--namespace",
            self.namespace,
            self.name,
            self.chart_path,
        ]
        render = subprocess.Popen(
            cmd,
            # stdin =subprocess.PIPE,
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=0,
        )

        with open(self.chart_path + "/manifest.yaml", "w") as f:
            f.write(render.stdout.read())

        render.wait()

    def Chart(self, scope: Construct, ns: str, **kwargs):
        self.render(self.values_path)
        # return HelmChart(
        #     scope,
        #     ns,
        #     source_file=self.chart_path + "/manifest.yaml",
        #     namespace=self.namespace,
        #     **kwargs,
        # )
        return HelmChart(
            scope,
            ns,
            source_file=self.chart_path + "/manifest.yaml",
            namespace=self.namespace,
            **kwargs,
        )

    def write_controls(self, outdir):
        script = (
            '#!/bin/bash\nNAMESPACE="'
            + self.namespace
            + '"\nCHART="'
            + self.chart
            + '"\nREPO="'
            + self.repo
            + '"\nNAME="'
            + self.name
            + '"\nVERSION="'
            + self.version
            + '"\nVALUES="'
            + os.path.abspath(self.values_path)
            + """
if [ -z "$1" ] || [ "$1" == "-h" ] || [ "$1" == "help" ]; then
  echo "$0 [command]"
  echo
  echo "All commands will be given the following options when applicable:"
  echo "  --namespace ${NAMESPACE}"
  echo "  --repo ${REPO}"
  echo "  --version ${VERSION}"
  echo "  --values ${VALUES}"
  echo "  [NAME] => ${NAME}"
  echo "  [CHART] => ${CHART}"
  echo "  [RELEASE] => ${NAME}"
  echo
  echo "All other given options will be appended"
  echo "Use -h as an appended option for any helm command"
  echo
  echo "Available Helm commands:"
  echo "  help"
  echo "  history"
  echo "  install"
  echo "  rollback"
  echo "  show all"
  echo "  show chart"
  echo "  show readme"
  echo "  show values"
  echo "  status"
  echo "  template"
  echo "  test"
  echo "  uninstall"
  echo "  upgrade"
  exit 0
fi
if [ "$1" == "history" ] || [ "$1" == "rollback" ] || [ "$1" == "status" ] || [ "$1" == "test" ] || [ "$1" == "uninstall" ]; then
  echo "$" helm "$1" --namespace "${NAMESPACE}" "${NAME}" "${@:2}"
  echo
  helm "$1" --namespace "${NAMESPACE}" "${NAME}" "${@:2}"
  exit 0
fi
if [ "$1" == "install" ] || [ "$1" == "template" ] || [ "$1" == "upgrade" ]; then
  echo "$" helm "$1" --namespace "${NAMESPACE}" --repo "${REPO}" --version "${VERSION}" --values "${VALUES}" "${NAME}" "${CHART}" "${@:2}"
  echo
  helm "$1" --namespace "${NAMESPACE}" --repo "${REPO}" --version "${VERSION}" --values "${VALUES}" "${NAME}" "${CHART}" "${@:2}"
  exit 0
fi
if [ "$1" == "show" ]; then
  if [ -z "$2" ]; then
    echo "Available show commands:"
    echo "  all"
    echo "  chart"
    echo "  readme"
    echo "  values"
    exit 0
  fi
  if [ "$2" == "all" ] || [ "$2" == "chart" ] || [ "$2" == "readme" ] || [ "$2" == "values" ]; then
    helm "$1" "$2" --namespace "${NAMESPACE}" --repo "${REPO}" --version "${VERSION}" "${CHART}" "${@:3}"
  fi
  exit 0
fi
echo "$1 is not a valid command"
exit 1
        """
        )
        # mkdir base dir just in case
        try:
            os.mkdir(outdir)
        except FileExistsError:
            {}
        # chmod +x
        script_file = outdir + "/" + self.name + ".sh"
        with open(script_file, "w") as f:
            f.write(script)
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IXUSR |
                 stat.S_IXGRP | stat.S_IXOTH)
