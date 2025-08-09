#!/usr/bin/env python3
"""
Sicherer Secret-Generator für VocalIQ
Generiert kryptographisch sichere Keys für Produktion
"""
import secrets
import string
import base64
from cryptography.fernet import Fernet


def generate_secret_key(length: int = 64) -> str:
    """Generiert einen sicheren Secret Key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret() -> str:
    """Generiert einen JWT-geeigneten Secret (URL-Safe Base64)"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')


def generate_encryption_key() -> str:
    """Generiert einen Fernet-Verschlüsselungsschlüssel"""
    return Fernet.generate_key().decode('utf-8')


def generate_admin_password() -> str:
    """Generiert ein sicheres Admin-Passwort"""
    return generate_secret_key(16)


if __name__ == "__main__":
    print("🔐 VocalIQ Secret Generator")
    print("=" * 50)
    
    secrets_dict = {
        "SECRET_KEY": generate_secret_key(),
        "JWT_SECRET_KEY": generate_jwt_secret(),
        "ENCRYPTION_KEY": generate_encryption_key(),
        "ADMIN_PASSWORD": generate_admin_password(),
        "DB_PASSWORD": generate_secret_key(20)
    }
    
    print("\n🔑 Generierte Secrets (SICHER AUFBEWAHREN!):")
    print("-" * 50)
    
    for key, value in secrets_dict.items():
        print(f"{key}={value}")
    
    # Erstelle env-Update Script
    env_updates = f'''
# Ersetze diese Werte in deiner .env Datei:
SECRET_KEY={secrets_dict["SECRET_KEY"]}
JWT_SECRET_KEY={secrets_dict["JWT_SECRET_KEY"]}
ADMIN_PASSWORD={secrets_dict["ADMIN_PASSWORD"]}
DATABASE_PASSWORD={secrets_dict["DB_PASSWORD"]}

# Neue Security-Variablen hinzufügen:
ENCRYPTION_KEY={secrets_dict["ENCRYPTION_KEY"]}
PASSWORD_HASH_ROUNDS=12
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900
'''
    
    with open('/tmp/vocaliq_secrets.env', 'w') as f:
        f.write(env_updates)
    
    print(f"\n💾 Secrets gespeichert in: /tmp/vocaliq_secrets.env")
    print("\n⚠️  WICHTIG:")
    print("1. Kopiere die generierten Werte in deine .env Datei")
    print("2. Lösche /tmp/vocaliq_secrets.env nach dem Kopieren")
    print("3. Teile diese Secrets NIE öffentlich!")
    print("4. Verwende für Produktion einen Secret Manager (z.B. HashiCorp Vault)")