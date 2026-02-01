import json
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.game import Game


def seed_games() -> None:
    games_path = Path(__file__).parent / "games.json"
    data = json.loads(games_path.read_text(encoding="utf-8"))

    with SessionLocal() as db:
        existing = {game.name: game for game in db.scalars(select(Game)).all()}
        for item in data:
            name = item["name"].strip()
            mode_icon = item.get("mode_icon")
            if name in existing:
                game = existing[name]
                game.mode_icon = mode_icon
                game.is_active = True
            else:
                db.add(Game(name=name, mode_icon=mode_icon, is_active=True))
        db.commit()


if __name__ == "__main__":
    seed_games()
    print("Games seeded")
