import hashlib, secrets, base64, json, time

def hash_password(password):
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),200000).hex()
    return salt+"$"+digest

def verify_password(password,stored):
    try:
        salt,digest=stored.split("$",1)
        return hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),200000).hex()==digest
    except Exception:
        return False

def make_token(user_id):
    payload={"sub":user_id,"exp":int(time.time())+86400}
    raw=base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return raw

def read_token(token):
    try:
        pad="="*((4-len(token)%4)%4)
        return json.loads(base64.urlsafe_b64decode((token+pad).encode()))
    except Exception:
        return None
