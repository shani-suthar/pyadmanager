# Security Policy

## Supported Versions

`pyadmanager` is pre-1.0 (currently `0.x`, Alpha). Only the latest version
published on [PyPI](https://pypi.org/project/pyadmanager/) is supported —
please upgrade before reporting an issue.

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities. Instead,
use GitHub's private reporting:

1. Go to the [Security tab](https://github.com/shani-suthar/pyadmanager/security) of this repository.
2. Click **Report a vulnerability**.

Alternatively, email shani.suthar98@gmail.com.

You should expect an initial response within a few days. This is a
solo-maintained open-source project without an SLA, but security reports are prioritized over other work.

## Scope Note

`pyadmanager` is a REST client — it does not store, transmit, or manage your
Google Ad Manager service account credentials beyond what you pass in
(`from_service_account_file`/`from_service_account_info`) for the lifetime of
your process. Never commit a real `creds.json`/service account key to a
repository or include one in a bug report; redact it first.
