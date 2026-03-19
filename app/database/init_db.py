from app.database.session import Base, engine
import app.models.alert
import app.models.log_entry
import app.models.user_profile


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
