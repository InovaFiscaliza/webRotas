# """
# Docker API client wrapper for container management and command execution.

# Provides a high-level interface for interacting with Docker containers,
# including fetching logs, running commands, and checking container status.
# """

# import docker
# from typing import Optional, Dict, Any, List
# from webrotas.config.logging_config import get_logger

# logger = get_logger(__name__)


# class DockerClientError(Exception):
#     """Base exception for Docker client operations."""
#     pass


# class ContainerNotFoundError(DockerClientError):
#     """Raised when a container cannot be found."""
#     pass


# class ContainerCommandError(DockerClientError):
#     """Raised when a command fails in a container."""
#     pass


# class DockerAPIClient:
#     """
#     High-level Docker API client for container operations.

#     Uses the official docker-py library to interact with Docker daemon
#     via the Docker API socket.
#     """

#     def __init__(self):
#         """Initialize Docker client."""
#         try:
#             self.client = docker.from_env()
#             logger.info("Docker client initialized successfully")
#         except Exception as e:
#             logger.error(f"Failed to initialize Docker client: {e}")
#             raise DockerClientError(f"Cannot connect to Docker daemon: {e}")

#     def get_container(self, container_name: str) -> docker.models.containers.Container:
#         """
#         Get a container by name.

#         Args:
#             container_name: Name of the container

#         Returns:
#             Docker container object

#         Raises:
#             ContainerNotFoundError: If container doesn't exist
#         """
#         try:
#             container = self.client.containers.get(container_name)
#             return container
#         except docker.errors.NotFound:
#             raise ContainerNotFoundError(f"Container '{container_name}' not found")
#         except Exception as e:
#             logger.error(f"Error getting container '{container_name}': {e}")
#             raise DockerClientError(f"Failed to get container: {e}")

#     def get_container_logs(
#         self,
#         container_name: str,
#         tail: int = 100,
#         follow: bool = False,
#     ) -> str:
#         """
#         Retrieve logs from a container.

#         Args:
#             container_name: Name of the container
#             tail: Number of lines to return from the end of the logs
#             follow: Whether to follow log output (not used for single fetch)

#         Returns:
#             Container logs as a string

#         Raises:
#             ContainerNotFoundError: If container doesn't exist
#             DockerClientError: If retrieval fails
#         """
#         try:
#             container = self.get_container(container_name)
#             logs = container.logs(tail=tail, follow=follow)

#             # Decode bytes to string if necessary
#             if isinstance(logs, bytes):
#                 logs = logs.decode('utf-8')

#             return logs
#         except ContainerNotFoundError:
#             raise
#         except Exception as e:
#             logger.error(f"Error retrieving logs from '{container_name}': {e}")
#             raise DockerClientError(f"Failed to get container logs: {e}")

#     def container_exists(self, container_name: str) -> bool:
#         """
#         Check if a container exists.

#         Args:
#             container_name: Name of the container

#         Returns:
#             True if container exists, False otherwise
#         """
#         try:
#             self.get_container(container_name)
#             return True
#         except ContainerNotFoundError:
#             return False
#         except Exception as e:
#             logger.warning(f"Error checking if container exists: {e}")
#             return False

#     def container_is_running(self, container_name: str) -> bool:
#         """
#         Check if a container is running.

#         Args:
#             container_name: Name of the container

#         Returns:
#             True if container is running, False otherwise
#         """
#         try:
#             container = self.get_container(container_name)
#             return container.status == "running"
#         except ContainerNotFoundError:
#             return False
#         except Exception as e:
#             logger.warning(f"Error checking container status: {e}")
#             return False

#     def exec_command(
#         self,
#         container_name: str,
#         command: str | List[str],
#         user: Optional[str] = None,
#         workdir: Optional[str] = None,
#     ) -> Dict[str, Any]:
#         """
#         Execute a command inside a running container.

#         Args:
#             container_name: Name of the container
#             command: Command to execute (string or list of strings)
#             user: User to run the command as (optional)
#             workdir: Working directory for the command (optional)

#         Returns:
#             Dictionary with keys:
#             - exit_code: Exit code of the command
#             - stdout: Standard output
#             - stderr: Standard error

#         Raises:
#             ContainerNotFoundError: If container doesn't exist
#             DockerClientError: If command execution fails
#         """
#         try:
#             container = self.get_container(container_name)

#             # Check if container is running
#             if not container.status == "running":
#                 raise DockerClientError(
#                     f"Container '{container_name}' is not running (status: {container.status})"
#                 )

#             # Prepare exec parameters
#             exec_params = {
#                 "cmd": command,
#                 "stdout": True,
#                 "stderr": True,
#             }

#             if user:
#                 exec_params["user"] = user

#             if workdir:
#                 exec_params["workdir"] = workdir

#             # Execute command
#             exec_result = container.exec_run(**exec_params)

#             # Decode output
#             output = exec_result.output.decode('utf-8') if isinstance(exec_result.output, bytes) else exec_result.output

#             return {
#                 "exit_code": exec_result.exit_code,
#                 "output": output,
#                 "stdout": output,  # Alias for backwards compatibility
#                 "stderr": "",  # Docker API returns combined output
#             }

#         except ContainerNotFoundError:
#             raise
#         except Exception as e:
#             logger.error(f"Error executing command in '{container_name}': {e}")
#             raise ContainerCommandError(f"Failed to execute command: {e}")

#     def list_containers(self, all: bool = False) -> List[Dict[str, Any]]:
#         """
#         List containers.

#         Args:
#             all: If False, list only running containers; if True, list all

#         Returns:
#             List of dictionaries with container info
#         """
#         try:
#             containers = self.client.containers.list(all=all)
#             return [
#                 {
#                     "id": c.id,
#                     "name": c.name,
#                     "status": c.status,
#                     "image": c.image.tags[0] if c.image.tags else c.image.id,
#                 }
#                 for c in containers
#             ]
#         except Exception as e:
#             logger.error(f"Error listing containers: {e}")
#             return []

#     def get_container_info(self, container_name: str) -> Dict[str, Any]:
#         """
#         Get detailed information about a container.

#         Args:
#             container_name: Name of the container

#         Returns:
#             Dictionary with container information

#         Raises:
#             ContainerNotFoundError: If container doesn't exist
#         """
#         try:
#             container = self.get_container(container_name)

#             return {
#                 "id": container.id,
#                 "name": container.name,
#                 "status": container.status,
#                 "image": container.image.tags[0] if container.image.tags else container.image.id,
#                 "created": container.attrs.get("Created"),
#                 "state": container.attrs.get("State"),
#                 "config": {
#                     "hostname": container.attrs["Config"].get("Hostname"),
#                     "ports": container.attrs["NetworkSettings"].get("Ports"),
#                 },
#             }
#         except ContainerNotFoundError:
#             raise
#         except Exception as e:
#             logger.error(f"Error getting container info: {e}")
#             raise DockerClientError(f"Failed to get container info: {e}")


# # Global client instance
# _docker_client: Optional[DockerAPIClient] = None


# def get_docker_client() -> DockerAPIClient:
#     """
#     Get or create the global Docker client instance.

#     Returns:
#         Singleton DockerAPIClient instance

#     Raises:
#         DockerClientError: If Docker daemon is not available
#     """
#     global _docker_client

#     if _docker_client is None:
#         _docker_client = DockerAPIClient()

#     return _docker_client
