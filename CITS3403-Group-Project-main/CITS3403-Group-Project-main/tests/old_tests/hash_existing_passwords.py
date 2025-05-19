# hash_existing_passwords.py

from app import create_app
from app.models import db, User
import hashlib

def is_hashed(pw):
    # SHA-256 hash is 64 hex characters long
    return len(pw) == 64 and all(c in '0123456789abcdef' for c in pw.lower())

app = create_app()

with app.app_context():
    users = User.query.all()
    updated = 0

    for user in users:
        if not is_hashed(user.password):
            original = user.password
            user.password = hashlib.sha256(original.encode()).hexdigest()
            updated += 1
            print(f"✅ Hashed password for: {user.email} (was: {original})")

    db.session.commit()
    print(f"\n🔐 Done. Updated {updated} user(s).")
