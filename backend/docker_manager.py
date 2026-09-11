import logging
import os
import secrets
from pathlib import Path
from typing import Optional

import docker
from docker.errors import DockerException, ImageNotFound, NotFound

log = logging.getLogger("docker-manager")

CHALLENGES_DIR = Path(__file__).parent / "challenges"
IMAGE_PREFIX = "avst-lite"
CONTAINER_PORT = 80

CATEGORIES = {
    "web": {"internal_port": CONTAINER_PORT, "label": "phantom-sandbox-web"},
    "iot": {"internal_port": CONTAINER_PORT, "label": "phantom-sandbox-iot"},
    "forensic": {"internal_port": CONTAINER_PORT, "label": "phantom-sandbox-forensic"},
}

_client: Optional[docker.DockerClient] = None
_sandboxes: dict = {}


def _candidate_hosts():
    if os.environ.get("DOCKER_HOST"):
        yield os.environ["DOCKER_HOST"]
    yield None  # let docker-py use its default resolution
    desktop_sock = Path.home() / ".docker" / "run" / "docker.sock"
    if desktop_sock.exists():
        yield f"unix://{desktop_sock}"


def get_client() -> Optional[docker.DockerClient]:
    global _client
    if _client is not None:
        return _client

    for host in _candidate_hosts():
        try:
            client = docker.DockerClient(base_url=host) if host else docker.from_env()
            client.ping()
            _client = client
            log.info("connected to docker at %s", host or "default")
            return _client
        except DockerException as exc:
            log.debug("docker host %s unavailable: %s", host, exc)

    log.warning("no docker daemon reachable; falling back to simulated mode")
    _client = None
    return None


def generate_flag(category: str) -> str:
    suffix = secrets.token_hex(4)
    return f"flag{{phantom_{category}_{suffix}}}"


def ensure_image(client: docker.DockerClient, category: str) -> str:
    tag = f"{IMAGE_PREFIX}-{category}:latest"
    try:
        client.images.get(tag)
    except ImageNotFound:
        log.info("building image %s", tag)
        client.images.build(path=str(CHALLENGES_DIR / category), tag=tag, rm=True)
    return tag


def start_sandbox(category: str) -> dict:
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")

    flag = generate_flag(category)
    client = get_client()

    if client is None:
        _sandboxes[category] = {"mode": "simulated", "flag": flag, "container_id": None, "port": None}
        return {"mode": "simulated", "flag": flag, "target": "172.28.0.10:8080 (simulated)", "port": None}

    stop_sandbox(category)
    tag = ensure_image(client, category)

    container = client.containers.run(
        tag,
        detach=True,
        environment={"FLAG": flag},
        ports={f"{CONTAINER_PORT}/tcp": None},
        name=f"{CATEGORIES[category]['label']}-{secrets.token_hex(3)}",
        remove=True,
    )
    container.reload()
    port_info = container.attrs["NetworkSettings"]["Ports"].get(f"{CONTAINER_PORT}/tcp")
    host_port = port_info[0]["HostPort"] if port_info else None

    _sandboxes[category] = {
        "mode": "docker",
        "flag": flag,
        "container_id": container.id,
        "port": host_port,
    }
    log.info("started %s sandbox container=%s port=%s", category, container.id[:12], host_port)
    return {"mode": "docker", "flag": flag, "target": f"127.0.0.1:{host_port}", "port": host_port}


def stop_sandbox(category: str) -> None:
    existing = _sandboxes.get(category)
    if not existing or existing.get("mode") != "docker":
        return
    client = get_client()
    if client is None:
        return
    try:
        c = client.containers.get(existing["container_id"])
        c.stop(timeout=2)
    except (NotFound, DockerException):
        pass


def get_sandbox(category: str) -> Optional[dict]:
    return _sandboxes.get(category)


def ping_verify(category: str, flag: str) -> None:
    """Ask the sandbox itself to check the flag, so a match creates a genuine
    server-side log entry for the Evidence Scanner to find (matters for
    challenges like forensics where the solve happens client-side)."""
    existing = _sandboxes.get(category)
    if not existing or existing.get("mode") != "docker":
        return
    import urllib.request
    import urllib.error
    import urllib.parse

    url = f"http://127.0.0.1:{existing['port']}/api/verify/{urllib.parse.quote(flag, safe='')}"
    try:
        urllib.request.urlopen(url, timeout=3).read()
    except (urllib.error.URLError, OSError):
        pass


def get_logs(category: str, tail: int = 50) -> str:
    existing = _sandboxes.get(category)
    if not existing or existing.get("mode") != "docker":
        return ""
    client = get_client()
    if client is None:
        return ""
    try:
        c = client.containers.get(existing["container_id"])
        return c.logs(tail=tail).decode(errors="ignore")
    except (NotFound, DockerException):
        return ""
