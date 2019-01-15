#!/usr/bin/env python3
import os
import traceback
import typing
import sys

import apscheduler.schedulers.blocking
import googleapiclient.discovery
import prometheus_client

HTTP_SERVER_PORT = 8000
TIMESTAMP_METRIC_NAME = "gcloud_exporter_last_update_unixtime"


def create_metric_name(resource: str, kind: str) -> str:
    return f'gcloud_{resource.lower()}_quota_{kind}'


def usage_ratio(usage: float, limit: float) -> float:
    return 0.0 if limit <= 0 else usage/limit


class QuotaUpdater:
    """
    Container object for the GCP API client and Prometheus metrics.

    """
    def __init__(self, project_id: str, compute_client: googleapiclient.discovery.Resource):
        self.project_id = project_id
        self.compute_client = compute_client
        self.metrics: typing.Dict[str, prometheus_client.core.Gauge] = {}
        self.registry = prometheus_client.CollectorRegistry(auto_describe=True)

    def run(self):
        """
        Updates all the metrics.
        """
        try:
            self.update_regional_quotas()
            self.update_global_quotas()
            self.update_timestamp()
        except Exception:
            print("Exception occurred while updating quotas data:")
            print(traceback.format_exc())

    def update_timestamp(self):
        if TIMESTAMP_METRIC_NAME not in self.metrics:
            self.metrics[TIMESTAMP_METRIC_NAME] = prometheus_client.Gauge(
                TIMESTAMP_METRIC_NAME,
                "Date of last successful quotas data update as unix timestamp/epoch",
                registry=self.registry)
        self.metrics[TIMESTAMP_METRIC_NAME].set_to_current_time()

    def update_regional_quotas(self):
        api_result = self.compute_client.regions().list(project=self.project_id, fields='items(name,quotas)').execute()
        for region in api_result['items']:
            self.publish_region_quotas(region)

    def update_global_quotas(self):
        api_result = self.compute_client.projects().get(
            project=self.project_id, fields='quotas').execute()
        self.publish_global_quotas(api_result['quotas'])

    def publish_region_quotas(self, region: dict):
        """
            region = {
                'name': 'asia-east1',
                'quotas': [
                    {'limit': 72.0, 'metric': 'CPUS', 'usage': 0.0},
                    ...
                ]
            }
        """
        for quota in region['quotas']:
            for kind in ('limit', 'usage'):
                self.publish_value(quota[kind], quota['metric'], kind, self.project_id, region['name'])
            self.publish_value(
                usage_ratio(quota['usage'], quota['limit']), quota['metric'],
                'ratio', self.project_id, region['name'])

    def publish_global_quotas(self, quotas: list):
        """
        quotas = [
            {'limit': 5000.0, 'metric': 'SNAPSHOTS', 'usage': 527.0},
            {'limit': 15.0, 'metric': 'NETWORKS', 'usage': 2.0},
            ...
        ]
        """
        for quota in quotas:
            for kind in ('limit', 'usage'):
                self.publish_value(quota[kind], quota['metric'], kind, self.project_id)
            self.publish_value(
                usage_ratio(quota['usage'], quota['limit']), quota['metric'], 'ratio', self.project_id)

    def publish_value(self, value: float, resource: str, kind: str, project_id: str, region: str = 'global'):
        metric_name = create_metric_name(resource, kind)

        if metric_name not in self.metrics:
            self.metrics[metric_name] = prometheus_client.Gauge(
                metric_name, f'Google Cloud quota for {resource} resource', ['project_id', 'region'],
                registry=self.registry)

        self.metrics[metric_name].labels(project_id=project_id, region=region).set(float(value))

    def serve(self):
        """
        Starts a non-blocking HTTP server serving the prometheus metrics
        """
        prometheus_client.start_http_server(HTTP_SERVER_PORT, registry=self.registry)


def main():
    try:
        gcloud_project_id = os.environ['QE_PROJECT_ID']
    except KeyError:
        print('QE_PROJECT_ID must be defined')
        sys.exit(1)

    try:
        refresh_interval_seconds = int(os.getenv('QE_REFRESH_INTERVAL', 60))
    except TypeError:
        print('QE_REFRESH_INTERVAL must be a number')
        sys.exit(1)

    print('Initialization..')
    compute = googleapiclient.discovery.build('compute', 'v1')
    quota_updater = QuotaUpdater(gcloud_project_id, compute)

    scheduler = apscheduler.schedulers.blocking.BlockingScheduler()
    scheduler.add_job(quota_updater.run, trigger='interval', seconds=refresh_interval_seconds, timezone='UTC')

    print('Verifying permissions..')
    quota_updater.run()

    quota_updater.serve()

    print('Starting scheduler')
    scheduler.start()


if __name__ == "__main__":
    main()
