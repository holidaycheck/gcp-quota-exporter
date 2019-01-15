import exporter

import prometheus_client


def test_publish_region_quotas():
    client = None
    updater = exporter.QuotaUpdater('foo', client)
    region = {
        'name': 'asia-east1',
        'quotas': [
            {'metric': 'BAR', 'limit': 10.0, 'usage': 1.0},
            {'metric': 'ZORK', 'limit': 10.0, 'usage': 4.0},
        ]
    }
    expected = """
# HELP gcloud_bar_quota_limit Google Cloud quota for BAR resource
# TYPE gcloud_bar_quota_limit gauge
gcloud_bar_quota_limit{project_id="foo",region="asia-east1"} 10.0
# HELP gcloud_bar_quota_usage Google Cloud quota for BAR resource
# TYPE gcloud_bar_quota_usage gauge
gcloud_bar_quota_usage{project_id="foo",region="asia-east1"} 1.0
# HELP gcloud_bar_quota_ratio Google Cloud quota for BAR resource
# TYPE gcloud_bar_quota_ratio gauge
gcloud_bar_quota_ratio{project_id="foo",region="asia-east1"} 0.1
# HELP gcloud_zork_quota_limit Google Cloud quota for ZORK resource
# TYPE gcloud_zork_quota_limit gauge
gcloud_zork_quota_limit{project_id="foo",region="asia-east1"} 10.0
# HELP gcloud_zork_quota_usage Google Cloud quota for ZORK resource
# TYPE gcloud_zork_quota_usage gauge
gcloud_zork_quota_usage{project_id="foo",region="asia-east1"} 4.0
# HELP gcloud_zork_quota_ratio Google Cloud quota for ZORK resource
# TYPE gcloud_zork_quota_ratio gauge
gcloud_zork_quota_ratio{project_id="foo",region="asia-east1"} 0.4
""".lstrip().encode('utf-8')

    updater.publish_region_quotas(region)

    assert prometheus_client.generate_latest(updater.registry) == expected


def test_publish_global_quotas():
    client = None
    updater = exporter.QuotaUpdater('foo', client)
    quotas = [
        {'metric': 'BAR', 'limit': 10.0, 'usage': 1.0},
        {'metric': 'ZORK', 'limit': 10.0, 'usage': 4.0},
    ]
    expected = """
# HELP gcloud_bar_quota_limit Google Cloud quota for BAR resource
# TYPE gcloud_bar_quota_limit gauge
gcloud_bar_quota_limit{project_id="foo",region="global"} 10.0
# HELP gcloud_bar_quota_usage Google Cloud quota for BAR resource
# TYPE gcloud_bar_quota_usage gauge
gcloud_bar_quota_usage{project_id="foo",region="global"} 1.0
# HELP gcloud_bar_quota_ratio Google Cloud quota for BAR resource
# TYPE gcloud_bar_quota_ratio gauge
gcloud_bar_quota_ratio{project_id="foo",region="global"} 0.1
# HELP gcloud_zork_quota_limit Google Cloud quota for ZORK resource
# TYPE gcloud_zork_quota_limit gauge
gcloud_zork_quota_limit{project_id="foo",region="global"} 10.0
# HELP gcloud_zork_quota_usage Google Cloud quota for ZORK resource
# TYPE gcloud_zork_quota_usage gauge
gcloud_zork_quota_usage{project_id="foo",region="global"} 4.0
# HELP gcloud_zork_quota_ratio Google Cloud quota for ZORK resource
# TYPE gcloud_zork_quota_ratio gauge
gcloud_zork_quota_ratio{project_id="foo",region="global"} 0.4
""".lstrip().encode('utf-8')

    updater.publish_global_quotas(quotas)

    assert prometheus_client.generate_latest(updater.registry) == expected
