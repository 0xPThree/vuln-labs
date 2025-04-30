#!/usr/bin/env python3
"""
Usage:
    python3 createHash.py Leonhard Euler 11122023
    User hash: de7834ea8e5d46f324f8ebd90fc0e4ce087ce819f2a1143aa8fb415975466523
"""

import hashlib

def generate_hash(first_name, last_name, date):
    # Concatenate first name, last name, and date
    full_name = first_name + last_name
    # Reverse the full name and append the date
    string_to_hash = full_name[::-1] + date
    # Generate SHA-256 hash
    sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
    return sha256_hash

# Take input arguments for first name, last name, and date
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python3 hash.py <firstname> <lastname> <date>")
        sys.exit(1)
    
    first_name = sys.argv[1]
    last_name = sys.argv[2]
    date = sys.argv[3]

    user_hash = generate_hash(first_name, last_name, date)
    print(f"User hash: {user_hash}")
