""" This module provides password checker"""

import sys
import requests
import hashlib


class checker():

    """ this is password checker class """

    def req_data(self, query_char):
        url = "https://api.pwnedpasswords.com/range/" + query_char
        req = requests.get(url)

        if req.status_code != 200:
            raise RuntimeError(
                f"Error fetching : {req.status_code}, check ur api again")
        return req

    def get_pwd_hack_count(self, hash, hash_to_check):
        hashes = (line.split(":") for line in hash.text.splitlines())
        for h, count in hashes:
            if h == hash_to_check:
                return count
        return 0

    def api_check(self, password):
        sha1pwd = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        first_5_char, tail = sha1pwd[:5], sha1pwd[5:]
        response = self.req_data(first_5_char)
        return self.get_pwd_hack_count(response, tail)

    def main(self, *args):
        """ 
        password checker main function.

        Parameters:
        args : no of passwords

        Returns:
        str: no of time pwd hacked
        """
        for passwords in args:
            count = self.api_check(passwords)
            if count:
                print(f"{passwords} was found {count} times... should change ur pwd")
            else:
                print(f"{passwords} was NOT found.. Carry on!!!")

        return "Done"
