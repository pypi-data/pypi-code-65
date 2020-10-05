import tempfile
from traxible.traxodule import Traxodule
from traxible.utils import htpasswd


class Nginx(Traxodule):
    def install(self):
        self.run(["sudo apt install -y nginx certbot python3-certbot-nginx"])

    def add_docker(self, domain, docker_ip, basic_auth=None):

        basic_auth_config = ""
        if basic_auth is not None:
            filepath = f"/etc/nginx/{domain}"
            htpasswd(
                user=basic_auth["user"],
                password=basic_auth["password"],
                filepath=filepath,
            )
            htpasswd_path = filepath
            basic_auth_config = f"""
            auth_basic           “Administrator’s Area”;
            auth_basic_user_file {htpasswd_path};
            """

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
        with tempfile.NamedTemporaryFile(mode="w") as file_pointer:
            file_pointer.write(new_conf)
            file_pointer.flush()
            self.put(file_pointer.name, f"/etc/nginx/sites-enabled/{domain}", sudo=True)

    def certbot(self, domain, mail):
        self.run(
            [
                f"sudo certbot --nginx  --non-interactive"
                f"--redirect --agree-tos -m {mail} --domains {domain}"
            ]
        )

    def restart(self):
        self.run(["sudo service nginx restart"])
