import logging
from app.sync_engine import GitSyncEngine
from app.runtime_driver import DockerRuntimeDriver
from app.diff_engine import DiffEngine

logger = logging.getLogger("reconciler")

class Reconciler:
    """Core GitOps reconciliation loop with robust atomic swap and rollback."""

    def __init__(self):
        self.git_engine = GitSyncEngine()
        self.driver = DockerRuntimeDriver()
        self.diff_engine = DiffEngine()

    def reconcile(self, commit_sha: str | None = None, manifest_path: str = "manifests/sample-app.yaml") -> dict:
        logger.info("Starting reconciliation loop...")
        
        # 1. Sync Git and extract Desired State
        self.git_engine.sync_repository(commit_sha)
        desired = self.git_engine.parse_manifest(manifest_path)

        # 2. Query Docker Engine for Actual State
        actual = self.driver.get_actual_state(desired.app_name)

        # 3. Calculate Drift
        drift = self.diff_engine.calculate_drift(desired, actual)
        if not drift.has_drift:
            logger.info("System is in sync. No drift detected.")
            return {"status": "in_sync", "drift": False}

        logger.warning(f"Drift detected: {drift.reasons}")

        # 4. Pull target image
        try:
            self.driver.pull_image(desired.image, desired.tag)
        except Exception as pull_err:
            logger.error(f"Image pull failed: {pull_err}")
            return {"status": "failed", "reason": "image_pull_failed"}

        # 5. Atomic Blue-Green / Candidate Deployment
        backup_container = None
        if actual.container_id:
            try:
                # Rename current active container to -backup to avoid name collision
                backup_container = self.driver.client.containers.get(actual.container_id)
                backup_container.stop()
                backup_name = f"{desired.app_name}-backup"
                self.driver.remove_container(backup_name)
                backup_container.rename(backup_name)
            except Exception as e:
                logger.warning(f"Could not prepare backup container: {e}")

        try:
            logger.info("Deploying candidate container...")
            new_id = self.driver.deploy_container(desired)

            # 6. Readiness Probe
            probe_port = desired.healthcheck_port or (desired.ports[0].host_port if desired.ports else None)
            if probe_port and desired.healthcheck_path:
                healthy = self.driver.wait_for_health(probe_port, desired.healthcheck_path)
                if not healthy:
                    raise RuntimeError(f"Readiness probe failed on port {probe_port}{desired.healthcheck_path}")

            # 7. Verification Succeeded: Remove backup
            if backup_container:
                logger.info("New workload healthy. Cleaning up backup container...")
                self.driver.remove_container(backup_container.id)

            logger.info("Workload deployed and verified successfully.")
            return {"status": "reconciled", "new_container_id": new_id}

        except Exception as err:
            logger.error(f"Deployment failed / Healthcheck failed: {err}. Initiating AUTO-ROLLBACK...")
            
            # Remove failed candidate
            self.driver.remove_container(desired.app_name)

            # Restore backup container
            if backup_container:
                try:
                    logger.warning("Restoring backup container...")
                    backup_container.rename(desired.app_name)
                    backup_container.start()
                    logger.info("Rollback successful. Previous container restored.")
                except Exception as rollback_err:
                    logger.critical(f"Fatal: Rollback failed: {rollback_err}")

            return {"status": "rollback_executed", "error": str(err)}