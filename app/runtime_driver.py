from socket import timeout
import time
import httpx
import docker
from docker.errors import NotFound, APIError
from app.models import DesiredState, ActualState, ContainerPortMapping
from app.config import settings

class DockerRuntimeDriver:
    """Interacts with Docker Engine to inspect, pull, deploy, and verify containers."""

    def __init__(self):
        self.client = docker.from_env()

    def get_actual_state(self, app_name: str) -> ActualState:
        try:
            container = self.client.containers.get(app_name)
            raw_image = container.image.tags[0] if container.image.tags else "unknown:unknown"
            image_name, tag = raw_image.split(":") if ":" in raw_image else (raw_image, "latest")

            # Extract port bindings
            ports = []
            port_bindings = container.attrs.get("HostConfig", {}).get("PortBindings", {}) or {}
            for c_port_proto, h_bindings in port_bindings.items():
                c_port = int(c_port_proto.split("/")[0])
                if h_bindings:
                    h_port = int(h_bindings[0]["HostPort"])
                    ports.append(ContainerPortMapping(container_port=c_port, host_port=h_port))

            return ActualState(
                container_id=container.id,
                app_name=app_name,
                image=image_name,
                tag=tag,
                ports=ports,
                status=container.status
            )
        except NotFound:
            return ActualState(app_name=app_name, image="", tag="", status="not_found")

    def pull_image(self, image: str, tag: str) -> None:
        self.client.images.pull(f"{image}:{tag}")

    def deploy_container(self, desired: DesiredState, container_name_override: str | None = None) -> str:
        name = container_name_override or desired.app_name
        port_dict = {f"{p.container_port}/{p.protocol}": p.host_port for p in desired.ports}

        container = self.client.containers.run(
            image=f"{desired.image}:{desired.tag}",
            name=name,
            ports=port_dict,
            environment=desired.env,
            detach=True
        )
        return container.id

    def wait_for_health(self, host_port: int, path: str = "/healthz") -> bool:
        """Polls the container endpoint to verify readiness."""
        url = f"http://localhost:{host_port}{path}"
        start_time = time.time()
        timeout = 6

        while time.time() - start_time < settings.HEALTHCHECK_TIMEOUT_SEC:
            try:
                response = httpx.get(url, timeout=2.0)
                if response.status_code == 200:
                    return True
            except (httpx.ConnectError, httpx.TimeoutException):
                pass
            time.sleep(settings.HEALTHCHECK_INTERVAL_SEC)
        return False

    def remove_container(self, name_or_id: str, force: bool = True) -> None:
        try:
            container = self.client.containers.get(name_or_id)
            container.remove(force=force)
        except NotFound:
            pass