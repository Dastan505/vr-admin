import argparse

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.models.user import User
from app.seed.init_defaults import init_defaults


def create_owner(email: str, password: str) -> User:
    location, _ = init_defaults()
    email = email.strip().lower()

    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            existing.password_hash = hash_password(password)
            existing.role = UserRole.owner
            existing.location_id = location.id
            db.commit()
            db.refresh(existing)
            return existing

        owner = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.owner,
            location_id=location.id,
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        return owner


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update owner user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    owner = create_owner(args.email, args.password)
    print(f"Owner ready: {owner.id} {owner.email}")


if __name__ == "__main__":
    main()
