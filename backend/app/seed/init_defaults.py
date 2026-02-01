from app.core.config import settings
from app.db.session import SessionLocal
from app.models.location import Location
from app.models.resource import Resource


def init_defaults() -> tuple[Location, Resource]:
    with SessionLocal() as db:
        location = db.query(Location).filter(Location.name == settings.ADMIN_DEFAULT_LOCATION).first()
        if not location:
            location = Location(name=settings.ADMIN_DEFAULT_LOCATION)
            db.add(location)
            db.commit()
            db.refresh(location)

        resource = (
            db.query(Resource)
            .filter(Resource.location_id == location.id, Resource.name == settings.DEFAULT_RESOURCE_NAME)
            .first()
        )
        if not resource:
            resource = Resource(location_id=location.id, name=settings.DEFAULT_RESOURCE_NAME)
            db.add(resource)
            db.commit()
            db.refresh(resource)

        return location, resource


if __name__ == "__main__":
    location, resource = init_defaults()
    print(f"Default location: {location.id} {location.name}")
    print(f"Default resource: {resource.id} {resource.name}")
