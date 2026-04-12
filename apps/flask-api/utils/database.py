"""
Database Utilities - Transaction Management & Query Optimization
Industry-standard patterns for Flask-SQLAlchemy
"""
from contextlib import contextmanager
from functools import wraps
from sqlalchemy.orm import joinedload
from models import db
import logging

logger = logging.getLogger(__name__)


@contextmanager
def atomic_transaction():
    """
    Atomic transaction context manager.
    Automatically commits on success, rolls back on exception.
    
    Usage:
        with atomic_transaction():
            db.session.add(obj)
            # Auto-committed if no exception
    """
    try:
        with db.session.begin():
            yield
    except Exception:
        logger.error("Transaction failed, rolled back", exc_info=True)
        raise


def transactional(f):
    """
    Decorator to wrap function in atomic transaction.
    
    Usage:
        @transactional
        def create_user(data):
            user = User(**data)
            db.session.add(user)
            return user
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        with atomic_transaction():
            return f(*args, **kwargs)
    return wrapper


def with_eager_load(*relationships):
    """
    Decorator to add eager loading to query functions.
    Prevents N+1 query problems.
    
    Usage:
        @with_eager_load('program', 'user', 'payments')
        def get_application(id):
            return Application.query.get(id)
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get the base query from the function
            result = f(*args, **kwargs)
            
            # If result is a query object, apply eager loading
            if hasattr(result, 'options'):
                for rel in relationships:
                    result = result.options(joinedload(rel))
            return result
        return wrapper
    return decorator


def get_or_404(model, id, eager_load=None):
    """
    Get model by ID or raise 404.
    Optional eager loading of relationships.
    
    Args:
        model: SQLAlchemy model class
        id: Primary key value
        eager_load: List of relationship names to eager load
    
    Returns:
        Model instance or raises NotFoundError
    """
    query = db.session.query(model)
    
    if eager_load:
        for rel in eager_load:
            query = query.options(joinedload(rel))
    
    result = query.get(id)
    
    if result is None:
        from utils.error_handlers import NotFoundError
        raise NotFoundError(f"{model.__name__} not found")
    
    return result


def paginate(query, page=1, per_page=20, max_per_page=100):
    """
    Safe pagination with limits.
    
    Args:
        query: SQLAlchemy query
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum allowed per_page
    
    Returns:
        Pagination object with items, total, pages
    """
    per_page = min(per_page, max_per_page)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def exists_query(model, **filters):
    """
    Efficient existence check.
    Returns True if any record matches filters.
    
    Usage:
        if exists_query(User, email='test@example.com'):
            # Handle duplicate
    """
    return db.session.query(
        db.session.query(model).filter_by(**filters).exists()
    ).scalar()


class QueryOptimizer:
    """
    Query optimization helpers for common patterns.
    """
    
    @staticmethod
    def select_in_batches(query, batch_size=1000):
        """
        Memory-efficient batch processing for large datasets.
        Yields items in batches to avoid loading all into memory.
        """
        offset = 0
        while True:
            batch = query.limit(batch_size).offset(offset).all()
            if not batch:
                break
            for item in batch:
                yield item
            offset += batch_size
    
    @staticmethod
    def bulk_insert(model, data_list, batch_size=1000):
        """
        Efficient bulk insert with batching.
        """
        from sqlalchemy import insert
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            db.session.execute(insert(model), batch)
        db.session.commit()
