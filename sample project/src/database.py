"""
Database operations and connection management
Using SQLAlchemy with SQLite for simplicity
"""

import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Optional
import structlog
from .models import User, UserCreate, UserUpdate
import os

logger = structlog.get_logger()

DATABASE_URL = "sample_api.db"


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_path: str = DATABASE_URL):
        self.db_path = db_path
    
    async def init_database(self):
        """Initialize database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    age INTEGER,
                    city TEXT,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            await db.commit()
            logger.info("Database tables created successfully")
    
    async def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        password_hash = f"hashed_{user.password}"  # In real app, use proper hashing
        now = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO users (email, name, age, city, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user.email, user.name, user.age, user.city, password_hash, now, now))
            
            user_id = cursor.lastrowid
            await db.commit()
            
            return User(
                id=user_id,
                email=user.email,
                name=user.name,
                age=user.age,
                city=user.city,
                created_at=now,
                updated_at=now,
                is_active=True
            )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT id, email, name, age, city, created_at, updated_at, is_active
                FROM users WHERE id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return User(
                        id=row['id'],
                        email=row['email'],
                        name=row['name'],
                        age=row['age'],
                        city=row['city'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        is_active=bool(row['is_active'])
                    )
                return None
    
    async def get_all_users(self) -> List[User]:
        """Get all users"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT id, email, name, age, city, created_at, updated_at, is_active
                FROM users WHERE is_active = TRUE
                ORDER BY created_at DESC
            """) as cursor:
                rows = await cursor.fetchall()
                
                return [
                    User(
                        id=row['id'],
                        email=row['email'],
                        name=row['name'],
                        age=row['age'],
                        city=row['city'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        is_active=bool(row['is_active'])
                    )
                    for row in rows
                ]
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user by ID"""
        # First check if user exists
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            return None
        
        # Build update query dynamically
        updates = []
        values = []
        
        if user_update.email is not None:
            updates.append("email = ?")
            values.append(user_update.email)
        if user_update.name is not None:
            updates.append("name = ?")
            values.append(user_update.name)
        if user_update.age is not None:
            updates.append("age = ?")
            values.append(user_update.age)
        if user_update.city is not None:
            updates.append("city = ?")
            values.append(user_update.city)
        
        if not updates:
            return existing_user  # No updates needed
        
        updates.append("updated_at = ?")
        values.append(datetime.now())
        values.append(user_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                UPDATE users 
                SET {', '.join(updates)}
                WHERE id = ?
            """, values)
            await db.commit()
        
        # Return updated user
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        """Soft delete user by setting is_active to False"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                UPDATE users 
                SET is_active = FALSE, updated_at = ?
                WHERE id = ? AND is_active = TRUE
            """, (datetime.now(), user_id))
            await db.commit()
            
            return cursor.rowcount > 0
    
    async def count_users(self) -> int:
        """Count active users"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0


# Global database manager instance
db_manager = DatabaseManager()


async def init_db():
    """Initialize database"""
    await db_manager.init_database()


async def get_db():
    """Dependency to get database manager"""
    return db_manager
