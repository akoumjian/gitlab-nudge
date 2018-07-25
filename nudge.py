import json
import click
import requests
import pendulum


class NudgeClient:
    def __init__(self, gitlab_host=None, gitlab_token=None, slack_uri=None, project_id=None):
        self.gitlab_host = gitlab_host
        self.gitlab_token = gitlab_token
        self.slack_uri = slack_uri
        self.project_id = project_id

    def gitlab_request(self, path="/", method="get", **kwargs):
        headers = {"Private-Token": self.gitlab_token}
        url = requests.compat.urljoin(self.gitlab_host, path)
        resp = requests.request(method=method, url=url, headers=headers, verify=False, **kwargs)
        return resp

    def get_open_mrs(self):
        path = "api/v4"
        if self.project_id:
            path = "{}/projects/{}".format(path, self.project_id)
        path = "{}/merge_requests".format(path)
        data = {
            "state": "opened",
            "scope": "all",
            "order_by": "created_at",
            "sort": "asc",
            "per_page": 100
        }
        resp = self.gitlab_request(
            method='get',
            path=path,
            data=data
        )
        open_requests = resp.json()
        return open_requests

    def post_to_slack(self, content):
        headers = {
            'content-type': 'application/json'
        }

        resp = requests.post(self.slack_uri, headers=headers, data=json.dumps(content))
        return resp

    def format_message(self, open_requests):
        attachments = []
        for mr in open_requests:
            title = mr.get('title')
            created = pendulum.parse(mr.get('created_at'))
            days_open = pendulum.now().diff(created).in_days()

            # Filter out new MRs
            if days_open < 1:
                continue

            # Filter out WIP
            if mr.get('work_in_progress'):
                continue

            labels = mr.get('labels')
            labels = ", ".join([label for label in labels])

            # Color code based on how old it is
            color = "#439FE0"
            if days_open > 3:
                color = "warning"
            if days_open > 7:
                color = "danger"

            # Hotfix should be priority
            if 'hotfix' in title.lower():
                color = "danger"

            assignee = mr.get('assignee')
            if assignee:
                assignee = assignee.get('name')

            author = mr.get('author')
            if author:
                author = author.get('name')

            attachment = {
                "fallback": title,
                "title": title,
                "title_link": mr.get('web_url'),
                "color": color,
                "fields": [
                    {
                        "title": "Days Open",
                        "value": days_open,
                        "short": True
                    },
                    {
                        "title": "Labels",
                        "value": labels,
                        "short": True
                    },
                    {
                        "title": "Author",
                        "value": author,
                        "short": True
                    },
                    {
                        "title": "Assignee",
                        "value": assignee,
                        "short": True
                    },
                ]
            }
            attachments.append(attachment)
        message = {
            "attachments": attachments
        }
        return message

    def run(self):
        open_requests = self.get_open_mrs()
        content = self.format_message(open_requests)
        self.post_to_slack(content)


@click.command()
@click.option("--gitlab_host")
@click.option("--gitlab_token")
@click.option("--slack_uri")
@click.option("--project_id", type=int)
def run(gitlab_host, gitlab_token, slack_uri, project_id):
    """
    Notify a slack channel about open merge requests
    """
    client = NudgeClient(
        gitlab_host=gitlab_host,
        gitlab_token=gitlab_token,
        slack_uri=slack_uri,
        project_id=project_id
    )
    client.run()
