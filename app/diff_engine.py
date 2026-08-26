from app.models import DesiredState, ActualState, StateDiff

class DiffEngine:
    """Calculates differences between the declarative Git spec and the running container."""

    @staticmethod
    def calculate_drift(desired: DesiredState, actual: ActualState) -> StateDiff:
        reasons = []

        if actual.status != "running":
            reasons.append(f"Container is currently in '{actual.status}' state.")

        if desired.image != actual.image or desired.tag != actual.tag:
            reasons.append(f"Image tag mismatch: Desired [{desired.image}:{desired.tag}] vs Actual [{actual.image}:{actual.tag}]")

        # Check port configuration differences
        desired_ports = sorted([p.model_dump() for p in desired.ports], key=lambda x: x["host_port"])
        actual_ports = sorted([p.model_dump() for p in actual.ports], key=lambda x: x["host_port"])
        if desired_ports != actual_ports:
            reasons.append(f"Port mapping drift detected.")

        return StateDiff(has_drift=len(reasons) > 0, reasons=reasons)