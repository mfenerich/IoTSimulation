"""
Define shared dependencies for the FastAPI application.

Use these dependencies across routes or components to manage common requirements,
such as database connections.
"""

from fastapi import Depends

from app.db.connection import get_db

# Module-level variable to fix B008
db_dependency = Depends(get_db)


def get_dependencies(db=db_dependency):
    """
    Provide shared dependencies for FastAPI routes.

    Args:
        db: Dependency injection for the database session.

    Returns:
        The database session dependency.
    """
    return db
