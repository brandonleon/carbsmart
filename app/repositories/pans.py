from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import Pan
from app.models import PanCreate, PanUpdate


def list_pans(db: Session) -> list[Pan]:
    return list(db.execute(select(Pan).order_by(Pan.name)).scalars().all())


def get_pan(db: Session, pan_id: int) -> Pan | None:
    return db.get(Pan, pan_id)


def create_pan(db: Session, payload: PanCreate) -> Pan:
    pan = Pan(
        name=payload.name,
        weight_grams=payload.weight_grams,
        capacity_label=payload.capacity_label or "",
        notes=payload.notes,
    )
    db.add(pan)
    db.commit()
    db.refresh(pan)
    return pan


def update_pan(db: Session, pan: Pan, payload: PanUpdate) -> Pan:
    updates = payload.model_dump(exclude_unset=True)
    if "capacity_label" in updates and updates["capacity_label"] is None:
        updates["capacity_label"] = ""
    for key, value in updates.items():
        setattr(pan, key, value)

    db.commit()
    db.refresh(pan)
    return pan


def delete_pan(db: Session, pan: Pan) -> None:
    db.delete(pan)
    db.commit()
