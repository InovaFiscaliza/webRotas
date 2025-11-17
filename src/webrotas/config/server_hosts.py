"""
Server host configuration for webRotas.

This module manages host settings for different environments:
- Development: uses localhost/127.0.0.1
- Containerized: uses container hostnames (osrm, webrotas, etc.)

Environment variables:
- WEBROTAS_ENVIRONMENT: Set to 'development' or 'production' (default: 'development')
- OSRM_HOSTNAME: Custom OSRM container hostname (default: 'osrm' in production, 'localhost' in development)
- WEBROTAS_HOSTNAME: Custom webRotas server hostname (default: 'webrotas' in production, 'localhost' in development)
"""

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OSRM_PORT = int(os.getenv("OSRM_PORT", 5000))
WEBROTAS_PORT = int(os.getenv("WEBROTAS_PORT", 5002))


class ServerHosts:
    """Central configuration for server host addresses"""

    @staticmethod
    def get_environment() -> str:
        """
        Get the current environment from environment variable or default to development.

        Returns:
            str: Either 'development' or 'production'
        """
        env = os.getenv("WEBROTAS_ENVIRONMENT", "development").lower()
        return env if env in ["development", "production"] else "development"

    @staticmethod
    def is_containerized() -> bool:
        """Check if running in containerized environment"""
        return ServerHosts.get_environment() == "production"

    @staticmethod
    def get_osrm_host() -> str:
        """
        Get OSRM server hostname.

        Development: localhost (127.0.0.1)
        Production: osrm (container hostname)

        Returns:
            str: Hostname for OSRM server
        """
        if (osrm_hostname := os.getenv("OSRM_HOSTNAME")) is not None:
            return osrm_hostname

        return "osrm" if ServerHosts.is_containerized() else "localhost"

    @staticmethod
    def get_webrotas_host() -> str:
        """
        Get webRotas server hostname.

        Development: localhost (127.0.0.1)
        Production: webrotas (container hostname)

        Returns:
            str: Hostname for webRotas server
        """
        if (webrotas_hostname := os.getenv("WEBROTAS_HOSTNAME")) is not None:
            return webrotas_hostname

        return "webrotas" if ServerHosts.is_containerized() else "localhost"

    @staticmethod
    def get_webrotas_url() -> str:
        """
        Get webRotas server base URL.

        Returns:
            str: Full URL for webRotas server (e.g., http://localhost:5002 or http://webrotas:5002)
        """
        return f"http://{ServerHosts.get_webrotas_host()}:{WEBROTAS_PORT}"

    @staticmethod
    def get_osrm_url() -> str:
        """
        Get OSRM server base URL.

        Returns:
            str: Full URL for OSRM server (e.g., http://localhost:5000 or http://osrm:5000)
        """
        return f"http://{ServerHosts.get_osrm_host()}:{OSRM_PORT}"


# Convenience functions for direct import
def get_osrm_host() -> str:
    """Get OSRM server hostname"""
    return ServerHosts.get_osrm_host()


def get_webrotas_host() -> str:
    """Get webRotas server hostname"""
    return ServerHosts.get_webrotas_host()


def get_webrotas_url() -> str:
    """Get webRotas server URL"""
    return ServerHosts.get_webrotas_url()


def get_osrm_url() -> str:
    """Get OSRM server URL"""
    return ServerHosts.get_osrm_url()


def is_containerized() -> bool:
    """Check if running in containerized environment"""
    return ServerHosts.is_containerized()
