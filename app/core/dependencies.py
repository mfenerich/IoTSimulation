from db.connection import get_db
from fastapi import Depends

def get_dependencies(db=Depends(get_db)):
    return db
