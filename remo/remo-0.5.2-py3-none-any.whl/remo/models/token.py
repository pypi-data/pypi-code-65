import json

from django.db import models

from cryptography.fernet import Fernet

from remo_app.remo.models import Key


class Token(models.Model):
    token = models.CharField(max_length=250)
    license = models.TextField(blank=True, null=True, default='')

    class Meta:
        db_table = 'tokens'

    def save(self, **kwargs):
        if self.license and '{' in self.license:
            cipher = self.get_cipher()
            enc_license = cipher.encrypt(self.license.encode())
            self.license = enc_license.decode()
        super().save(**kwargs)

    def get_cipher(self) -> Fernet:
        db_key = Key.objects.first()
        if db_key:
            key = db_key.key.encode()
        else:
            key = Fernet.generate_key()
            Key.objects.create(key=key.decode())
        return Fernet(key)

    def get_license(self) -> dict:
        if not self.license:
            return {}

        if '{' in self.license:
            self.save()

        return json.loads(
            self.get_cipher().decrypt(self.license.encode()).decode()
        )

