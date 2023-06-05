import json
import logging
import os

from google.cloud import tasks_v2


class CloudTask:
    def __init__(self):
        self.task_client = tasks_v2.CloudTasksClient()
        self.task_parent = self.task_client.queue_path(
            'precise-line-76299minutos',
            'us-central1',
            'p2p-analysis'
        )

    async def create_task(self, base_url, endpoint, request_payload={}):
        if 'localhost' not in base_url:
            base_url = base_url.replace("http://", "https://")

        task = {
            "http_request": {
                "headers": {
                    "Content-Type": "application/json"
                },
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{base_url}{endpoint.strip('/')}",
            }
        }
        payload = json.dumps(request_payload)
        task["http_request"]["body"] = payload.encode()

        response = self.task_client.create_task(request={"parent": self.task_parent, "task": task})
        print("Created task {}".format(response.name))
