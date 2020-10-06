import tempfile
from traxible.traxodule import Traxodule
from traxible.utils import htpasswd


class Nginx(Traxodule):
    def install(self):
        self.run(["sudo apt install -y nginx certbot python3-certbot-nginx"])

    def add_docker(self, domain, docker_ip, basic_auth=None):

        basic_auth_config = ""
        if basic_auth is not None:
            htpass_file = tempfile.NamedTemporaryFile(mode="w")
            htpasswd(
                user=basic_auth["user"],
                password=basic_auth["password"],
                filepath=htpass_file.name,
            )
            basic_auth_config = f"""
auth_basic           "Administrator’s Area";
auth_basic_user_file "/etc/nginx/{domain}";
"""

            self.put(htpass_file.name, f"/etc/nginx/{domain}", sudo=True)

        new_conf = f"""
server {{
    index index.html index.htm;
    server_name {domain};
    
    location / {{
        {basic_auth_config}
        proxy_pass http://{docker_ip}:4242;
        proxy_redirect off;
        proxy_set_header Host $host;
    }}

    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;

}}
"""
        with tempfile.NamedTemporaryFile(mode="w") as nginx_conf:
            nginx_conf.write(new_conf)
            nginx_conf.flush()
            self.put(nginx_conf.name, f"/etc/nginx/sites-enabled/{domain}", sudo=True)

    def certbot(self, domain, mail):
        self.run(
            [
                f"sudo certbot --nginx  --non-interactive"
                f"--redirect --agree-tos -m {mail} --domains {domain}"
            ]
        )

    def restart(self):
        self.run(["sudo service nginx restart"])
