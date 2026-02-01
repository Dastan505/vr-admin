from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_owner
from app.db.session import get_db
from app.models.game import Game
from app.schemas.game import GameCreate, GameOut, GameUpdate

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=list[GameOut])
def list_games(
    active_only: bool = True,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[GameOut]:
    query = db.query(Game)
    if active_only:
        query = query.filter(Game.is_active.is_(True))
    return query.order_by(Game.name.asc()).all()


@router.post("", response_model=GameOut, status_code=status.HTTP_201_CREATED)
def create_game(
    payload: GameCreate,
    db: Session = Depends(get_db),
    user=Depends(require_owner),
) -> GameOut:
    exists = db.query(Game).filter(Game.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Game already exists")
    game = Game(name=payload.name, mode_icon=payload.mode_icon)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.put("/{game_id}", response_model=GameOut)
def update_game(
    game_id: int,
    payload: GameUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_owner),
) -> GameOut:
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if payload.name is not None:
        game.name = payload.name
    if payload.mode_icon is not None:
        game.mode_icon = payload.mode_icon
    if payload.is_active is not None:
        game.is_active = payload.is_active
    db.commit()
    db.refresh(game)
    return game


@router.delete("/{game_id}")
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_owner),
) -> dict:
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    db.delete(game)
    db.commit()
    return {"status": "deleted"}
