#!/usr/bin/env python
"""GroupBite – secret / key initialiser.

Generates VAPID keys, a Fernet encryption key, and a Flask SECRET_KEY,
then optionally writes them to the .env file.  When an existing FERNET_KEY
is being replaced the tool re-encrypts all database rows that were
encrypted with the old key before saving the new one.
"""

import base64
import secrets
import sys
from pathlib import Path

import ecdsa
from cryptography.fernet import Fernet
from dotenv import dotenv_values

ENV_FILE = Path(".env")


# ── Key generators ──────────────────────────────────────────────────────────

def gen_vapid_keys():
    pri = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    pub = pri.get_verifying_key()
    return (
        base64.urlsafe_b64encode(pri.to_string()).decode().rstrip("="),
        base64.urlsafe_b64encode(b"\x04" + pub.to_string()).decode().rstrip("="),
    )


def gen_fernet_key():
    return Fernet.generate_key().decode()


def gen_secret_key():
    return secrets.token_hex(32)


# ── .env helpers ────────────────────────────────────────────────────────────

def read_env():
    if ENV_FILE.exists():
        return dotenv_values(ENV_FILE)
    return {}


def backup_env():
    """Copy .env to .env.backup.<timestamp> if it exists and has content."""
    if not ENV_FILE.exists() or not ENV_FILE.read_text().strip():
        return None
    from datetime import datetime
    backup = ENV_FILE.with_name(f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup.write_text(ENV_FILE.read_text())
    return backup


def write_env(updates: dict, any_overwrite: bool = False):
    """Merge *updates* into .env, preserving all other lines and comments.
    Creates a timestamped backup first if any existing value is being overwritten."""
    if any_overwrite:
        backup = backup_env()
        if backup:
            print(f"  Backup written to {backup}")
    lines = ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []
    written = set()
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                result.append(f"{key}={updates[key]}")
                written.add(key)
                continue
        result.append(line)
    for key, val in updates.items():
        if key not in written:
            result.append(f"{key}={val}")
    ENV_FILE.write_text("\n".join(result) + "\n")


# ── Re-encryption ────────────────────────────────────────────────────────────

def reencrypt_database(old_key: str, new_key: str, db_url: str):
    from cryptography.fernet import Fernet as F
    from sqlalchemy import create_engine, text

    old_cipher = F(old_key.encode())
    new_cipher = F(new_key.encode())

    def reenc(raw: str) -> str:
        decrypted = old_cipher.decrypt(base64.b64decode(raw))
        return base64.b64encode(new_cipher.encrypt(decrypted)).decode()

    engine = create_engine(db_url)
    with engine.begin() as conn:
        # notification table: p256dh, auth
        rows = conn.execute(
            text("SELECT vendor_id, user_id, endpoint, p256dh, auth FROM notification")
        ).fetchall()
        reenc_count = 0
        for row in rows:
            try:
                new_p256dh = reenc(row.p256dh)
                new_auth = reenc(row.auth)
                conn.execute(
                    text(
                        "UPDATE notification SET p256dh=:p, auth=:a "
                        "WHERE vendor_id=:v AND user_id=:u AND endpoint=:e"
                    ),
                    {
                        "p": new_p256dh,
                        "a": new_auth,
                        "v": str(row.vendor_id),
                        "u": str(row.user_id),
                        "e": row.endpoint,
                    },
                )
                reenc_count += 1
            except Exception as exc:
                print(f"  [warn] could not re-encrypt notification row: {exc}")

        print(f"  Re-encrypted {reenc_count} notification row(s).")

        # setting table: smtp_password
        smtp_rows = conn.execute(
            text("SELECT value FROM setting WHERE key='smtp_password'")
        ).fetchall()
        for row in smtp_rows:
            if row.value:
                try:
                    new_val = reenc(row.value)
                    conn.execute(
                        text("UPDATE setting SET value=:v WHERE key='smtp_password'"),
                        {"v": new_val},
                    )
                    print("  Re-encrypted smtp_password setting.")
                except Exception as exc:
                    print(f"  [warn] could not re-encrypt smtp_password: {exc}")


# ── Prompts ──────────────────────────────────────────────────────────────────

def ask(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt} [y/N] ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("", "n", "no"):
            return False


def resolve(env: dict, key: str, new_val: str, label: str):
    """Return (value_to_write_or_None, overwriting_existing)."""
    existing = env.get(key, "").strip()
    if existing:
        print(f"  {label}: already set.")
        if ask(f"  Overwrite {key}?"):
            return new_val, True
        return None, False
    return new_val, False


def _db_url(env: dict) -> str:
    user = env.get("POSTGRES_USER", "groupbite")
    pw = env.get("POSTGRES_PASSWORD", "groupbite")
    host = env.get("POSTGRES_HOST", "localhost")
    port = env.get("POSTGRES_PORT", "5432")
    name = env.get("POSTGRES_DB_NAME", "groupbite")
    return f"postgresql://{user}:{pw}@{host}:{port}/{name}"


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("GroupBite – secret / key initialiser")
    print("=" * 40)

    env = read_env()
    updates = {}
    any_overwrite = False

    # ── VAPID keys ──────────────────────────────────────────────────────────
    print("\n[VAPID keys]")
    priv_b64, pub_b64 = gen_vapid_keys()
    already_set = env.get("VAPID_PRIVATE_KEY", "").strip() or env.get("VAPID_PUBLIC_KEY", "").strip()
    if already_set:
        print("  VAPID keypair: already set.")
        print("  WARNING: rotating VAPID keys invalidates all existing push subscriptions.")
        print("           Users will not receive notifications until they re-subscribe.")
        write_vapid = ask("  Overwrite VAPID keypair (both keys)?")
    else:
        write_vapid = True
    if write_vapid:
        updates["VAPID_PRIVATE_KEY"] = priv_b64
        updates["VAPID_PUBLIC_KEY"] = pub_b64
        if already_set:
            any_overwrite = True
            updates["_wipe_notifications"] = True

    vapid_email = env.get("VAPID_SUBJECT_EMAIL", "").strip()
    if not vapid_email:
        vapid_email = input("\n  VAPID subject e-mail (e.g. admin@example.com): ").strip()
        if vapid_email:
            updates["VAPID_SUBJECT_EMAIL"] = vapid_email

    # ── Fernet key ──────────────────────────────────────────────────────────
    print("\n[Fernet encryption key]")
    print("  NOTE: if overwritten, all encrypted database values will be automatically re-encrypted.")
    new_fernet = gen_fernet_key()
    fernet_val, fernet_overwritten = resolve(env, "FERNET_KEY", new_fernet, "FERNET_KEY")
    if fernet_overwritten:
        any_overwrite = True
        old_fernet = env["FERNET_KEY"]
        db_url = _db_url(env)
        print(f"\n  Re-encrypting database rows (DB: {db_url}) …")
        try:
            reencrypt_database(old_fernet, new_fernet, db_url)
        except Exception as exc:
            print(f"\n  [ERROR] Re-encryption failed: {exc}")
            print("  The .env file has NOT been updated. Fix the issue and retry.")
            sys.exit(1)
    if fernet_val:
        updates["FERNET_KEY"] = fernet_val

    # ── Flask SECRET_KEY ────────────────────────────────────────────────────
    print("\n[Flask SECRET_KEY]")
    new_secret = gen_secret_key()
    secret_val, secret_overwritten = resolve(env, "SECRET_KEY", new_secret, "SECRET_KEY")
    if secret_overwritten:
        any_overwrite = True
    if secret_val:
        updates["SECRET_KEY"] = secret_val

    # ── Write ────────────────────────────────────────────────────────────────
    wipe_notifications = updates.pop("_wipe_notifications", False)

    if not updates:
        print("\nNothing to update – all keys are already set.")
        return

    print(f"\nThe following keys will be written to {ENV_FILE}:")
    for k in updates:
        print(f"  {k}")
    if wipe_notifications:
        print("  (notification table will be wiped)")

    if ask("\nWrite to .env?"):
        write_env(updates, any_overwrite=any_overwrite)
        if wipe_notifications:
            db_url = _db_url(env)
            try:
                from sqlalchemy import create_engine, text
                with create_engine(db_url).begin() as conn:
                    result = conn.execute(text("DELETE FROM notification"))
                    print(f"  Wiped {result.rowcount} notification subscription(s).")
            except Exception as exc:
                print(f"  [warn] Could not wipe notification table: {exc}")
        print("Done.")
    else:
        print("\nGenerated values (not saved):")
        for k, v in updates.items():
            print(f"  {k}={v}")


if __name__ == "__main__":
    main()
