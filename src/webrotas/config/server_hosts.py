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
from enum import Enum


class Environment(Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"  # or containerized environments


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
    def get_webrotas_url(port: int) -> str:
        """
        Get webRotas server base URL.

        Args:
            port (int): Server port number

        Returns:
            str: Full URL for webRotas server (e.g., http://localhost:5002 or http://webrotas:5002)
        """
        return f"http://{ServerHosts.get_webrotas_host()}:{port}"

    @staticmethod
    def get_osrm_url(port: int) -> str:
        """
        Get OSRM server base URL.

        Args:
            port (int): Server port number (typically 5000)

        Returns:
            str: Full URL for OSRM server (e.g., http://localhost:5000 or http://osrm:5000)
        """
        return f"http://{ServerHosts.get_osrm_host()}:{port}"


# Convenience functions for direct import
def get_osrm_host() -> str:
    """Get OSRM server hostname"""
    return ServerHosts.get_osrm_host()


def get_webrotas_host() -> str:
    """Get webRotas server hostname"""
    return ServerHosts.get_webrotas_host()


def get_webrotas_url(port: int) -> str:
    """Get webRotas server URL"""
    return ServerHosts.get_webrotas_url(port)


def get_osrm_url(port: int) -> str:
    """Get OSRM server URL"""
    return ServerHosts.get_osrm_url(port)


def is_containerized() -> bool:
    """Check if running in containerized environment"""
    return ServerHosts.is_containerized()
