# Gitlab Nudge

Remind everyone about open Merge Requests. It queries your Gitlab setup for open Merge Requests and posts them to a Slack channel.

Usage:

nudge   --gitlab_host [your gitlab hostname] \
        --gitlab_token [gitlab personal access token] \
        --slack_uri [Slack Webhook Uri] \
        --project_id [Optional project ID in gitlab]

