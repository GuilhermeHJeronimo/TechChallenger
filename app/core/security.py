import hashlib

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password_provided: str, hashed_password_from_db: str) -> bool:
    current_password_hash = get_password_hash(plain_password_provided)

    print(f"SECURITY_UTILS (hashlib_verify): Plain='{plain_password_provided}'")
    print(f"SECURITY_UTILS (hashlib_verify): GeneratedHash='{current_password_hash}'")
    print(f"SECURITY_UTILS (hashlib_verify): StoredHash='{hashed_password_from_db}'")
    return current_password_hash == hashed_password_from_db