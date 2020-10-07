from fire import Fire

from traxible.traxible import Traxible
from traxible.docker import Docker
from traxible.deb import Deb
from traxible.nginx import Nginx
from traxible.utils import ip_in_cidr


DEFAULT_PACKAGES = "tree ncdu fail2ban vim nano grep tmux"


def setup_web_site(
    self,
    host,
    network_name="my_network",
    cidr="172.42.0.0/16",
    domain="example.com",
    mail="no-reply@exmaple.com",
):
    traxible = Traxible(host)

    # setup machine
    deb = Deb(traxible)
    deb.update()
    deb.install(DEFAULT_PACKAGES)

    # install docker
    docker = Docker(traxible)
    docker.install()
    traxible.reconnect()
    docker.list()
    docker.network(network_name, cidr)
    docker_ip = ip_in_cidr(cidr)
    docker.create(
        name="my_docker",
        image="my_image:latest",
        network_name=network_name,
        port_expose=8080,
        ip=docker_ip,
    )

    # install and configure nginx
    nginx = Nginx(traxible)
    nginx.install()
    nginx.add_docker(domain, docker_ip)
    nginx.certbot(domain, mail)
    nginx.restart()


if __name__ == "__main__":
    Fire()
