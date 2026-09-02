#!/usr/bin/env python3
"""
Cifra/decifra data/registro.csv <-> data/registro.csv.enc

Formato compatibile con la dashboard (WebCrypto): AES-256-GCM,
chiave derivata con PBKDF2-HMAC-SHA256 (310000 iterazioni).
La password si digita a schermo (getpass): non compare mai in chiaro,
non viene salvata da nessuna parte.

Uso:
  python3 tools/cifra.py            # cifra registro.csv -> registro.csv.enc
  python3 tools/cifra.py --decifra  # decifra registro.csv.enc -> registro.csv

Richiede il pacchetto 'cryptography':  pip3 install cryptography
"""
import os, sys, json, base64, hashlib, getpass, argparse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE, "data", "registro.csv")
ENC_PATH = os.path.join(BASE, "data", "registro.csv.enc")
ITER = 310000

def _aesgcm():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM
    except ImportError:
        sys.exit("Manca il pacchetto 'cryptography'. Installa con:\n  pip3 install cryptography")

def derive(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITER, dklen=32)

def encrypt(text, password):
    AESGCM = _aesgcm()
    salt = os.urandom(16); iv = os.urandom(12)
    ct = AESGCM(derive(password, salt)).encrypt(iv, text.encode("utf-8"), None)
    return json.dumps({"v":1,"kdf":"PBKDF2","hash":"SHA-256","iter":ITER,
                       "cipher":"AES-256-GCM",
                       "salt":base64.b64encode(salt).decode(),
                       "iv":base64.b64encode(iv).decode(),
                       "ct":base64.b64encode(ct).decode()}) + "\n"

def decrypt(blob, password):
    AESGCM = _aesgcm()
    o = json.loads(blob)
    key = derive(password, base64.b64decode(o["salt"]))
    pt = AESGCM(key).decrypt(base64.b64decode(o["iv"]), base64.b64decode(o["ct"]), None)
    return pt.decode("utf-8")

def main():
    ap = argparse.ArgumentParser(description="Cifra/decifra il registro")
    ap.add_argument("--decifra", action="store_true", help="da .enc a .csv in chiaro")
    a = ap.parse_args()

    if a.decifra:
        if not os.path.exists(ENC_PATH): sys.exit(f"Non trovo {ENC_PATH}")
        pw = getpass.getpass("Password: ")
        try:
            text = decrypt(open(ENC_PATH, encoding="utf-8").read(), pw)
        except Exception:
            sys.exit("Password errata o file danneggiato.")
        open(CSV_PATH, "w", encoding="utf-8", newline="").write(text)
        print(f"OK -> {CSV_PATH} (in chiaro). Ricorda di NON committarlo.")
    else:
        if not os.path.exists(CSV_PATH): sys.exit(f"Non trovo {CSV_PATH}")
        pw = getpass.getpass("Nuova password: ")
        if len(pw) < 8: sys.exit("Password troppo corta (min 8).")
        if getpass.getpass("Ripeti password: ") != pw: sys.exit("Le password non coincidono.")
        blob = encrypt(open(CSV_PATH, encoding="utf-8").read(), pw)
        open(ENC_PATH, "w", encoding="utf-8").write(blob)
        print(f"OK -> {ENC_PATH} (cifrato). Ora puoi cancellare data/registro.csv in chiaro.")

if __name__ == "__main__":
    main()
