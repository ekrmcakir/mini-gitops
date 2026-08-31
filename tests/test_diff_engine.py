from app.models import DesiredState, ActualState
from app.diff_engine import DiffEngine

def test_diff_engine_no_drift():
    desired = DesiredState(app_name="app1", image="nginx", tag="alpine")
    actual = ActualState(app_name="app1", image="nginx", tag="alpine", status="running")

    diff = DiffEngine.calculate_drift(desired, actual)
    assert diff.has_drift is False

def test_diff_engine_tag_drift():
    desired = DesiredState(app_name="app1", image="nginx", tag="1.25")
    actual = ActualState(app_name="app1", image="nginx", tag="1.24", status="running")

    diff = DiffEngine.calculate_drift(desired, actual)
    assert diff.has_drift is True
    assert any("Image tag mismatch" in r for r in diff.reasons)
