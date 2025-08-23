"""
Pydantic models for API data validation and serialization
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    age: Optional[int] = Field(None, ge=0, le=150, description="User age")
    city: Optional[str] = Field(None, max_length=100, description="User city")


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserUpdate(BaseModel):
    """Model for updating user information"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    city: Optional[str] = Field(None, max_length=100)


class User(UserBase):
    """Complete user model with database fields"""
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(True, description="User account status")

    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "john.doe@example.com",
                "name": "John Doe",
                "age": 30,
                "city": "New York",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00",
                "is_active": True
            }
        }


class ApiResponse(BaseModel):
    """Standard API response model"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Error details")
