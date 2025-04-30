#!/usr/bin/env python3
import socket
import dnslib
import sys
from dnslib import DNSRecord, DNSQuestion, RR, A
import logging

# Flag to control if queries should be printed to stdout
debug_mode = False

# Set up logging to log DNS queries to file
logging.basicConfig(filename='./dns-queries.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define a basic DNS handler
def handle_dns_query(data, addr):
    # Parse the DNS request
    request = DNSRecord.parse(data)
    query_name = str(request.q.qname)

    # Log the incoming query to the log file
    logging.info(f"Received DNS query: {query_name} from {addr}")

    # If in debug mode, also print to stdout
    if debug_mode:
        print(f"Received DNS query: {query_name} from {addr}")

    # Build a simple DNS response
    response = request.reply()
    response.add_answer(*RR.fromZone(f"{request.q.qname} 60 A 127.0.0.1"))  # Respond with 127.0.0.1

    # Send the response back to the client
    server_socket.sendto(response.pack(), addr)

# Set up the DNS server
def start_dns_server():
    # Define DNS server address (using 0.0.0.0 to bind to all available network interfaces)
    server_address = ('0.0.0.0', 53)  # Listening on all network interfaces on port 53 (DNS)

    # Create a UDP socket for DNS
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print("DNS server started. Listening for incoming DNS requests...")

    # Listen for incoming DNS requests and handle them
    while True:
        data, addr = server_socket.recvfrom(512)  # Buffer size for DNS queries
        handle_dns_query(data, addr)

if __name__ == "__main__":
    # Check for the -d flag to enable debug mode
    if '-d' in sys.argv:
        debug_mode = True
        print("Debug mode enabled. Queries will be printed to stdout.")

    # Start the DNS server
    start_dns_server()
