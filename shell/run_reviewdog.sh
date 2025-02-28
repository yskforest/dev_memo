#!/bin/bash

export REVIEWDOG_GITHUB_API_TOKEN=XXX
export CI_REPO_OWNER=$(gh repo view --json owner | jq -r '.owner.login')
export CI_REPO_NAME=$(gh repo view --json name | jq -r '.name')
export CI_COMMIT=$(git rev-parse origin/$(gh pr view --json headRefName | jq -r '.headRefName'))
export CI_PULL_REQUEST=$(gh pr view --json number | jq -r '.number')

echo "${CI_REPO_OWNER}, ${CI_REPO_NAME}, ${CI_COMMIT}, ${CI_PULL_REQUEST}"

# pylint test.py > report.txt
# textlint README.md  > report.txt

cat report.txt | ./bin/reviewdog -efm="%f:%l:%c: %m" -name="textlint" -reporter=github-pr-review -filter-mode=added -fail-on-error=false
