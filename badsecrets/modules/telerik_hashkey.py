import re
import hmac
import base64
import binascii
import urllib.parse
from badsecrets.base import BadsecretsBase


class Telerik_HashKey(BadsecretsBase):

    identify_regex = re.compile(r"^(?:[A-Za-z0-9+\/=%]+)$")

    def prepare_keylist(self):
        for l in self.load_resource("aspnet_machinekeys.txt"):
            try:
                vkey, ekey = l.rstrip().split(",")
                yield vkey
            except ValueError:
                continue
        for l in self.load_resource("telerik_hash_keys.txt"):
            vkey = l.strip()
            yield vkey

    def check_secret(self, dialogParameters_raw):

        dialogParametersB64 = urllib.parse.unquote(dialogParameters_raw)
        dp_enc = dialogParametersB64[:-44].encode()
        dp_hash = dialogParametersB64[-44:].encode()

        for vkey in self.prepare_keylist():
            try:
                h = hmac.new(vkey.encode(), dp_enc, self.hash_algs["SHA256"])
                if base64.b64encode(h.digest()) == dp_hash:
                    return {"Telerik.Upload.ConfigurationHashKey": vkey}
            except binascii.Error:
                continue
        return None