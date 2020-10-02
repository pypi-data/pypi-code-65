import tempfile
from traxible.traxodule import Traxodule


class Nginx(Traxodule):
    def install(self):
        self.run(["sudo apt install -y nginx certbot python3-certbot-nginx"])

    def add_docker(self, domain, docker_ip):
        new_conf = f"""
server {{
    index index.html index.htm;
    server_name {domain};

    location / {{
        proxy_pass http://{docker_ip}:4242;
        proxy_redirect off;
        proxy_set_header Host $host;
    }}

    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;

}}
"""
        with tempfile.NamedTemporaryFile(mode="w") as file:
            file.write(new_conf)
            file.flush()
            self.put(
                file.name,
                "/etc/nginx/sites-enabled/{domain}".format(domain=domain),
                sudo=True,
            )

    def certbot(self, domain, mail):
        self.run(
            [
                f"sudo certbot --nginx  --non-interactive"
                f"--redirect --agree-tos -m {mail} --domains {domain}"
            ]
        )

    def restart(self):
        self.run(["sudo service nginx restart"])
