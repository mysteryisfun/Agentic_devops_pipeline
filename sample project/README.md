# 🚀 Sample API - CI/CD Pipeline Testing Project

A comprehensive **FastAPI** sample application designed specifically for testing **CI/CD pipelines** and **Build Agents**. This project demonstrates real-world API development patterns with complete CRUD operations, database integration, and production-ready structure.

## 📋 Project Overview

This is a **real-world FastAPI application** that includes:

- ✅ **Complete CRUD API** with user management
- ✅ **Database integration** (SQLite with async operations)
- ✅ **Data validation** with Pydantic models  
- ✅ **Structured logging** with detailed API monitoring
- ✅ **Production-ready configuration** management
- ✅ **Comprehensive error handling**
- ✅ **API documentation** (Swagger/OpenAPI)
- ✅ **Multiple build configurations** (setup.py, pyproject.toml, Makefile)

## 🏗️ Architecture

```
src/
├── main.py          # FastAPI application with all endpoints
├── models.py        # Pydantic data models
├── database.py      # Database operations (SQLite + aiosqlite)
├── config.py        # Application settings and configuration
└── __init__.py      # Package initialization

tests/               # Test directory (for future Test Agent)
requirements.txt     # Python dependencies
setup.py            # Traditional Python packaging
pyproject.toml       # Modern Python packaging (PEP 518)
Makefile            # Build automation and common tasks
```

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint - health check |
| `GET` | `/health` | Detailed health check |
| `GET` | `/users` | Get all users |
| `POST` | `/users` | Create a new user |
| `GET` | `/users/{id}` | Get user by ID |
| `PUT` | `/users/{id}` | Update user |
| `DELETE` | `/users/{id}` | Delete user |
| `GET` | `/stats` | Application statistics |

## 🛠️ Build Agent Compatibility

This project is designed to work with **multiple build methods** that your Build Agent can detect:

### 1. **Requirements.txt** (Priority 1)
```bash
pip install -r requirements.txt
```

### 2. **Setup.py** (Priority 2)  
```bash
python setup.py build
python setup.py install
```

### 3. **Pyproject.toml** (Priority 3)
```bash
pip install -e .
```

### 4. **Makefile** (Priority 4)
```bash
make install    # Install dependencies
make build      # Build project
make run        # Run application
```

## 🚀 Quick Start

### Option 1: Using pip (Recommended)
```bash
pip install -r requirements.txt
python -m src.main
```

### Option 2: Using Make
```bash
make install
make run
```

### Option 3: Using setup.py
```bash
python setup.py install
python -m src.main
```

## 🧪 Testing the API

Once running (default: `http://localhost:8000`):

### 1. **Health Check**
```bash
curl http://localhost:8000/health
```

### 2. **Create a User**
```bash
curl -X POST "http://localhost:8000/users" \
-H "Content-Type: application/json" \
-d '{
  "email": "john.doe@example.com",
  "name": "John Doe",
  "age": 30,
  "city": "New York",
  "password": "securepassword123"
}'
```

### 3. **Get All Users**
```bash
curl http://localhost:8000/users
```

### 4. **API Documentation**
Visit: `http://localhost:8000/docs` (Swagger UI)

## 📊 Features for CI/CD Testing

### **Database Operations**
- ✅ **SQLite database** with async operations
- ✅ **User CRUD** operations
- ✅ **Data persistence** between runs
- ✅ **Error handling** for database failures

### **API Features**
- ✅ **FastAPI** with automatic API documentation
- ✅ **Pydantic validation** with detailed error messages
- ✅ **CORS middleware** for frontend integration
- ✅ **Structured logging** for monitoring

### **Build System**
- ✅ **Multiple build methods** (pip, setup.py, pyproject.toml, make)
- ✅ **Dependencies management** with requirements.txt
- ✅ **Development and production** configurations
- ✅ **Entry points** and console scripts

## 🔧 Available Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make build         # Build the project
make run           # Run the application
make test          # Run tests (when implemented)
make clean         # Clean build artifacts
make format        # Format code with black
make lint          # Run code linting
```

## 📱 Real-world Example Usage

This API simulates a **user management system** that you might find in production:

1. **User Registration** - POST new users with validation
2. **User Authentication** - Password hashing (simplified for demo)
3. **Profile Management** - Update user information
4. **User Directory** - List and search users
5. **Account Management** - Soft delete users

## 🎯 Perfect for Build Agent Testing

### **Why this project is ideal:**

1. **✅ Multiple Build Methods** - Tests agent's detection logic
2. **✅ Real Dependencies** - Tests package installation
3. **✅ Actual Database** - Tests runtime environment setup  
4. **✅ API Endpoints** - Tests application startup
5. **✅ Error Scenarios** - Tests error handling in build process
6. **✅ Production Structure** - Tests real-world project builds

### **Build Agent Test Scenarios:**
- ✅ Dependency installation from requirements.txt
- ✅ Python package building with setup.py
- ✅ Modern Python packaging with pyproject.toml
- ✅ Makefile-based build automation
- ✅ Application startup and health checks
- ✅ Database initialization and operations

## 🐛 Expected Build Agent Behavior

When your Build Agent encounters this project, it should:

1. **Detect** `requirements.txt` → Install dependencies
2. **Detect** `setup.py` or `pyproject.toml` → Build package  
3. **Detect** `Makefile` → Run make commands
4. **Start** the application → Verify it's running
5. **Test** endpoints → Ensure API responds correctly

## 🔍 Logging and Monitoring

The application includes comprehensive logging:
- ✅ **Structured logs** with timestamp and level
- ✅ **Database operation** logging
- ✅ **API request/response** logging  
- ✅ **Error tracking** with detailed stack traces

## 🌟 This is a Production-Quality Example

Unlike simple "Hello World" examples, this project includes:

- **Real database operations** with proper async handling
- **Complete error handling** and validation
- **Production-ready configuration** management
- **Comprehensive API documentation**
- **Multiple build system support**
- **Structured logging** and monitoring
- **Proper Python packaging** standards

Perfect for testing your **Build Agent's** capabilities with a **real-world application**! 🎯