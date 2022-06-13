import base64
import hashlib
import json
import requests

from Cryptodome import Random
from Cryptodome.Cipher import AES


class ProtectedTextApi:
    def __init__(self, site_id, passwd):
        self.siteHash = hashlib.sha512(("/" + site_id).encode("latin1")).hexdigest()
        self.pas = passwd
        self.passHash = hashlib.sha512(passwd.encode("latin1")).hexdigest()
        self.endpoint = "https://www.protectedtext.com/" + site_id
        self.siteObj = (requests.get(self.endpoint + "?action=getJSON")).json()
        self.dbversion = self.siteObj["currentDBVersion"]
        self.rawtext = decrypt(self.siteObj["eContent"], self.pas.encode())
        self.rawtext = self.rawtext[:len(self.rawtext) - 128]

    def save(self, textToSave):
        encript = str(textToSave + self.siteHash)
        textEncrypted = encrypt(encript, self.pas.encode())
        postdata = {"initHashContent": self.getWritePermissionProof(self.rawtext),
                    "currentHashContent": self.getWritePermissionProof(textToSave), "encryptedContent": textEncrypted,
                    "action": "save"}
        ret = (requests.post(self.endpoint, data=postdata, headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/73.0.3683.75 Safari/537.36 "
        })).text
        self.rawtext = textToSave
        return ret

    def deleteSite(self):
        inithashcontent = self.getWritePermissionProof(self.rawtext)
        deleteAction = {"initHashContent": inithashcontent, "action": "delete"}
        return (requests.post(self.endpoint, deleteAction)).json()

    def view(self):
        return self.rawtext

    def getWritePermissionProof(self, content):
        if self.dbversion == 1:
            return hashlib.sha512(f"{content}".encode("latin1")).hexdigest()
        else:
            return str(hashlib.sha512(f"{content}{self.passHash}".encode("latin1")).hexdigest()) + f"{self.dbversion}"


BLOCK_SIZE = 16


def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return (data + (chr(length) * length)).encode()


def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


def bytes_to_key(data, salt, output=48):
    assert len(salt) == 8, len(salt)
    data += salt
    key = hashlib.md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = hashlib.md5(key + data).digest()
        final_key += key
    return final_key[:output]


def encrypt(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message))).decode("utf-8")


def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:])).decode("utf-8")


class DB:
    def __init__(self, login: str, password: str) -> None:
        self.text = None
        self.login = login
        self.password = password

    @property
    def data(self) -> dict:
        self.text = ProtectedTextApi(self.login, self.password)
        return json.loads(self.text.view())

    def save(self, data) -> None:
        self.text.save(json.dumps(data))
