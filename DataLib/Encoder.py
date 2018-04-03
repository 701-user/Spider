from Crypto.Cipher import AES
import base64

class encoder():
    def __init__(self):
        self.key = 'Lima.maoblog#comi123@maoblog.com'
        self.mode = AES.MODE_ECB
    def encrypt(self, text):
        cryptor = AES.new(self.key,  mode=self.mode, IV="")
        length = 32
        count = len(text)
        if count % length != 0:
            add = length - (count % length)
        else:
            add = 0
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return base64.b64encode(self.ciphertext)

    # def decrypt(self, text):
    #     cryptor = AES.new(self.key, mode=self.mode)
    #     plain_text = cryptor.decrypt(base64.b64decode(text))
    #     plain_text = str(plain_text,"gbk")
    #     return plain_text

    def decrypt(self,enStr):
        cipher = AES.new(self.key, AES.MODE_ECB)
        enStr += (len(enStr) % 4) * "="
        decryptByts = base64.urlsafe_b64decode(enStr)
        msg = str(cipher.decrypt(decryptByts),"utf-8")
        paddingLen = ord(msg[len(msg) - 1])
        return msg[0:-paddingLen]