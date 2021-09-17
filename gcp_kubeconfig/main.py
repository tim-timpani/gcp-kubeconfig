import argparse
import logging

from google.auth import load_credentials_from_file
from google.auth.transport.requests import Request
from google.cloud.container_v1 import ClusterManagerClient
import yaml


class GkeApi:
    """Class for interacting with Google Cloud Compute (GCP) Kubernetes clusters."""

    def __init__(self, cluster_name: str, zone: str, sa_credentials_file_path: str):
        """GCP Demo for getting kubeconfig
        :param cluster_name: Name of the GKE cluster
        :param zone: Name of the Zone
        :param sa_credentials_file_path: Path to the service account credentials
        """
        self.cluster_name = cluster_name
        self._credentials, self.project_id = load_credentials_from_file(
            sa_credentials_file_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self.zone = zone

        # Generate the GCP Cluster Manager Client.
        # See: https://googleapis.dev/python/container/latest/container_v1/cluster_manager.html
        self.client = ClusterManagerClient(credentials=self.credentials)

    @property
    def parent(self):
        return f"projects/{self.project_id}/locations/{self.zone}"

    @property
    def credentials(self):
        if not self._credentials.valid or self._credentials.expired:
            self._credentials.refresh(Request())
        return self._credentials

    def get_cluster(self):
        return self.client.get_cluster(name=f"{self.parent}/clusters/{self.cluster_name}/nodePools/default-pool")

    @property
    def kubeconfig_dict(self) -> dict:
        cluster = self.get_cluster()
        config_id = f"gke_{self.project_id}_{cluster.zone}_{cluster.name}"
        return {
            'apiVersion': 'v1',
            'clusters': [
                {
                    'cluster': {
                        'certificate-authority-data': cluster.master_auth.cluster_ca_certificate,
                        'server': f"https://{cluster.endpoint}"
                    },
                    'name': config_id
                }
            ],
            'contexts': [
                {
                    'context': {
                        'cluster': config_id,
                        'user': config_id
                    },
                    'name': config_id
                }
            ],
            'current-context': config_id,
            'kind': 'Config',
            'preferences': {},
            'users': [
                {
                    'name': config_id,
                    'user': {
                        'auth-provider': {
                            'config': {
                                'access-token': self.credentials.token,
                                'cmd-args': 'config config-helper --format=json',
                                'cmd-path': 'gcloud',
                                'expiry': str(self.credentials.expiry),
                                'expiry-key': '{.credential.token_expiry}',
                                'token-key': '{.credential.access_token}'
                            },
                            'name': 'gcp'
                        }
                    }
                }
            ]
        }


def main():

    parser = argparse.ArgumentParser(description='Generate kubeconfig programmatically')
    parser.add_argument(
        'cluster',
        help='Name of the GKE cluster'
    )
    parser.add_argument(
        'zone',
        help='Zone the cluster is located in'
    )
    parser.add_argument(
        'credentials_file',
        help='Path to to service account credentials file'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Set logging to debug level'
    )
    args = parser.parse_args()

    # Configure logging
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    log_formatter = '%(asctime)s %(name)s %(levelname)s %(message)s'
    logging.basicConfig(format=log_formatter, level=log_level)

    # Instantiate the api for this cluster
    gke_api = GkeApi(cluster_name=args.cluster, zone=args.zone, sa_credentials_file_path=args.credentials_file)

    # Output is stdout
    print(yaml.safe_dump(gke_api.kubeconfig_dict, default_flow_style=False))


if __name__ == "__main__":
    main()
