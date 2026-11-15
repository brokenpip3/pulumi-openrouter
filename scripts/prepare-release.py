#!/usr/bin/env python3
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


SCHEMA_DIR = 'provider/cmd/pulumi-resource-openrouter/'
VERSION_ASSIGNMENT = re.compile(r'^(PROVIDER_VERSION[ \t]*\?=[ \t]*)[^\r\n]*', re.MULTILINE)


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()


def inputs():
    version = os.environ['RELEASE_VERSION']
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError('Version must be stable major.minor.patch without a leading v or leading zeroes.')
    ref = os.environ['GITHUB_REF']
    if not ref.startswith('refs/heads/'):
        raise ValueError('Select a repository branch, not a tag.')
    branch = ref.removeprefix('refs/heads/')
    if branch.startswith('-'):
        raise ValueError('Invalid branch name.')
    run('git', 'check-ref-format', ref)
    if run('git', 'rev-parse', 'HEAD') != os.environ['GITHUB_SHA']:
        raise ValueError('Checkout does not match the workflow source commit.')
    return version, branch


def prepare():
    version, _ = inputs()
    path = Path('Makefile')
    text = path.read_text()
    if len(VERSION_ASSIGNMENT.findall(text)) != 1:
        raise ValueError('Expected exactly one PROVIDER_VERSION ?= assignment in Makefile.')
    path.write_text(VERSION_ASSIGNMENT.sub(lambda match: match[1] + version, text))
    print(f'Prepared provider version {version}.')


def allowed(path):
    return path == 'Makefile' or path in {
        SCHEMA_DIR + 'schema.json', SCHEMA_DIR + 'bridge-metadata.json',
    } or path.startswith('sdk/')


def changed_paths(*args):
    # Keep NUL delimiters: generated paths can contain spaces and newlines.
    result = subprocess.run(['git', *args], check=True, capture_output=True, text=True)
    return set(result.stdout.rstrip('\0').split('\0')) if result.stdout else set()


def summary(message):
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as stream:
            stream.write(message + '\n')


def publish():
    version, base = inputs()
    tracked = changed_paths('diff', '--no-renames', '--name-only', '-z', 'HEAD', '--')
    unexpected = sorted(path for path in tracked if not allowed(path))
    if unexpected:
        raise ValueError('Unexpected tracked changes: ' + ', '.join(unexpected))
    untracked = changed_paths('ls-files', '--others', '--exclude-standard', '-z')
    paths = sorted(tracked | {path for path in untracked if allowed(path)})
    if not paths:
        summary('No changes to prepare; no branch or PR was created.')
        return

    source = os.environ['GITHUB_SHA']
    remote_base = run('git', 'ls-remote', '--exit-code', 'origin', 'refs/heads/' + base).split()[0]
    if remote_base != source:
        raise ValueError('Source branch moved during generation. Run the workflow again on its latest commit.')
    run_id = os.environ['GITHUB_RUN_ID']
    attempt = os.environ['GITHUB_RUN_ATTEMPT']
    if not re.fullmatch(r'[0-9]+', run_id) or not re.fullmatch(r'[0-9]+', attempt):
        raise ValueError('Invalid workflow run ID or attempt.')
    branch = f'automation/prepare-release-{version}-{run_id}-{attempt}'
    if run('git', 'ls-remote', 'origin', 'refs/heads/' + branch):
        raise ValueError('Automation branch already exists; rerun the workflow with a new attempt.')
    run('git', 'switch', '-c', branch)
    run('git', 'add', '-A', '--', *paths)
    run('git', '-c', 'user.name=github-actions[bot]',
        '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        '-c', 'commit.gpgsign=false', 'commit', '-m', f'Prepare provider v{version}')
    # An empty expected value makes this create-only, even if another process
    # creates the branch between ls-remote and push. Never overwrite a review.
    run('git', 'push', f'--force-with-lease=refs/heads/{branch}:',
        'origin', f'HEAD:refs/heads/{branch}')
    repository = os.environ['GITHUB_REPOSITORY']
    server = os.environ['GITHUB_SERVER_URL'].rstrip('/')
    run_url = f'{server}/{repository}/actions/runs/{run_id}'
    body = f'''Prepare provider **v{version}** from `{base}` at `{source}`.

Generated and built in [workflow run]({run_url}):

- `make tfgen`
- `make provider`
- `make build_sdks` (dotnet, Go, Node.js, Python)
- `make test_provider`

Review the Makefile, schema, and generated SDK changes. If GitHub shows
**Approve workflows to run**, approve the PR checks and wait for them to pass.

Merge this PR into `{base}`. If this is a feature branch, merge that branch
into the default branch before releasing. Tag the final release commit
`v{version}` and push the tag to start the existing release workflow.

No release tag or merge was performed by this workflow.
'''
    with tempfile.TemporaryDirectory() as directory:
        body_file = Path(directory) / 'pr-body.md'
        body_file.write_text(body)
        url = run('gh', 'pr', 'create', '--repo', repository, '--base', base, '--head', branch,
                  '--title', f'Prepare provider v{version}', '--body-file', str(body_file))
    summary(f'Created release preparation PR: {url}\n\nBuild and test run: {run_url}')


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'prepare', 'publish'}:
        raise ValueError('Usage: prepare-release.py prepare|publish')
    {'prepare': prepare, 'publish': publish}[sys.argv[1]]()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f'::error::{error}', file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr, file=sys.stderr)
        sys.exit(1)
