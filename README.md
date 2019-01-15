# GCP Quota Exporter

A [Prometheus](https://prometheus.io/) exporter for Google Cloud Platform resource quotas. Periodically refreshes the quotas for a specific GCP project and exposes them as metrics for consumption by Prometheus. Useful for visibility, tracking, and alerting in case of an impending quota depletion.

## Usage

We recommend that you use the exporter via its Docker image:

```shell
$ docker run -d \
    -v /path/to/private-key.json:/private-key.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/private-key.json \
    -e QE_PROJECT_ID=<project-id> \
    -p 8000:8000 \
    --name exporter \
    holidaycheck/gcp-quota-exporter
```

* `private-key.json` must be the private key of a GCP service account with the `servicemanagement.quotaViewer` role for the GCP project in question.
* The `GOOGLE_APPLICATION_CREDENTIALS` environment variable should point to the location inside the container where the private key was mounted.
* The `QE_PROJECT_ID` environment variable should be set to the GCP project ID whose quota you'd like to export.

In the above example, the exporter will be exposed at `http://<path-to-docker-host>:8000/metrics`. You can verify that the exporter is running correctly by running `curl 127.0.0.1:8000/metrics | tail`.

### Exported metrics

The following metrics are exported for each GCP resource quota in the project:

* `gcloud_[RESOURCE]_quota_limit` - Quota limit on this resource
* `gcloud_[RESOURCE]_quota_usage` - Current usage value of this resource
* `gcloud_[RESOURCE]_quota_ratio` - Resource utilization as a fraction of quota in use, e.g. `0.8` if 8 out of 10 is in use

As well as this metrics:

* `gcloud_exporter_last_update_unixtime` - When the quota information was last updated

## Contributing

If you want to contribute, feel free to open PRs in this repository. You can use `test_with_docker.sh` script to run all the tests in dedicated docker container.
