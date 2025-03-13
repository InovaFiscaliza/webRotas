#!/usr/bin/env python3
"""
Testa portas livres para uso pelo servidor
"""

import socket

# ----------------------------------------------------------------------------------------------
def is_port_available(port: int) -> bool:
    """Check if a port is available to use.
    
    :param port: Port number to check.
    :return: True if the port is available, False otherwise.
    """
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            return True
        except OSError:
            return False

# ----------------------------------------------------------------------------------------------
def find_available_port(start_port: int, port_step: int = 500, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port.
    
    :param start_port: Port number to start the search.
    :param port_step: Step to increment the port number. Default is 500.
    :param max_attempts: Maximum number of ports to check. Default is 100.
    :return: The first available port found or None if no port is available.
    """
    
    end_port = start_port + max_attempts * port_step
    if end_port > 65535:
        end_port = 65535
        
    for port in range(start_port, end_port, port_step):
        if is_port_available(port):
            return port
    return None

# ----------------------------------------------------------------------------------------------
def get_port(preferred_port:int) -> int:
    """Get an available port for the server.
    
    :param preferred_port: Preferred port to start the search.
    :return: An available port for the server.
    :raises ValueError: If no available port is found.
    """
    
    port = find_available_port(preferred_port)
    if port is None:
        raise ValueError("No available port found")
    return port