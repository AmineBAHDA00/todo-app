from .db import init_db, db
from .document import Document, DatabaseError

__all__ = ["init_db", "db", "Document", "DatabaseError"]  

