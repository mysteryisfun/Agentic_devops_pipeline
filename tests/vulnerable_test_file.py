#!/usr/bin/env python3
"""
Vulnerable Code Test File
This file contains intentional security vulnerabilities to test our AI analysis
"""

import os
import subprocess
import sqlite3

def vulnerable_login(username, password):
    """SQL Injection vulnerability"""
    # This should trigger HIGH severity SQL injection detection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    conn = sqlite3.connect('users.db')
    result = conn.execute(query).fetchone()
    return result

def vulnerable_command_execution(user_input):
    """Command Injection vulnerability"""
    # This should trigger HIGH severity command injection detection
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout

def vulnerable_file_access(filename):
    """Path Traversal vulnerability"""
    # This should trigger MEDIUM severity path traversal detection
    with open(f"uploads/{filename}", "r") as f:
        return f.read()

def insecure_password_check(password):
    """Weak password validation"""
    # This should trigger LOW-MEDIUM severity quality issue
    if len(password) > 4:
        return True
    return False

class VulnerableAPI:
    """Class with multiple security issues"""
    
    def __init__(self):
        self.secret_key = "hardcoded_secret_123"  # Hardcoded secret
    
    def process_data(self, data):
        """Dangerous eval usage"""
        # This should trigger HIGH severity code execution
        result = eval(data)
        return result
    
    def log_user_input(self, user_data):
        """XSS vulnerability in logging"""
        # This should trigger MEDIUM severity XSS
        log_message = f"<div>User input: {user_data}</div>"
        print(log_message)
        return log_message

if __name__ == "__main__":
    # Test the vulnerable functions
    print("Testing vulnerable functions...")
    
    # These should all be flagged by our AI analysis
    vulnerable_login("admin'; DROP TABLE users; --", "any_password")
    vulnerable_command_execution("rm -rf /")
    vulnerable_file_access("../../../etc/passwd")
    insecure_password_check("123")
    
    api = VulnerableAPI()
    api.process_data("__import__('os').system('rm -rf /')")
    api.log_user_input("<script>alert('XSS')</script>")
