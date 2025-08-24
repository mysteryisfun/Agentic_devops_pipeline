## 📋 Essential Files for Successful Build Agent Run

Based on our Build Agent requirements, here are the **exact files** needed in a target project:

### **Minimum Required Files:**

#### **1. Python Dependencies**
```
requirements.txt          # MUST HAVE - for pip install
```

#### **2. Python Source Code**
```
src/                      # Source directory
├── __init__.py          # Makes it a package
├── main.py              # Entry point
└── (any other .py files)
```
OR
```
*.py files in root       # Alternative structure
```

#### **3. Build Configuration (Optional but Recommended)**
```
setup.py                 # For python setup.py build
pyproject.toml           # Modern Python packaging
Makefile                 # For make commands
```

### **Complete Example Project Structure:**

````
my-test-api/
├── requirements.txt     # Dependencies (ESSENTIAL)
├── setup.py            # Build script (RECOMMENDED)
├── README.md           # Documentation
├── src/                # Source code
│   ├── __init__.py
│   ├── main.py         # FastAPI/Flask app
│   ├── models.py       # Data models
│   └── utils.py        # Helper functions
├── tests/              # Test directory (for Test Agent later)
│   ├── __init__.py
│   └── test_main.py
└── .gitignore          # Git ignore file
````

### **Essential File Contents:**

#### **requirements.txt** (MUST HAVE):
````
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
````

#### **setup.py** (RECOMMENDED):
````python
from setuptools import setup, find_packages

setup(
    name="my-test-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
    ]
)
````

#### **main.py** (SAMPLE):
````python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
````

### **Build Agent Detection Logic:**

Our Build Agent will look for files in this order:
1. ✅ **requirements.txt** → Run `pip install -r requirements.txt`
2. ✅ **setup.py** → Run `python setup.py build`
3. ✅ **pyproject.toml** → Run `pip install -e .`
4. ✅ **Makefile** → Run `make build` or `make install`
5. ✅ **Any .py files** → Run `python -m py_compile`

### **Minimum for Testing:**
Just create a repo with:
- requirements.txt 
- main.py (simple Python file)

**Should I create a sample test repository with this exact structure for you to test against?**