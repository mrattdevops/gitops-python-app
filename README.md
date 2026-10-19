# Application configuration

The Python application reads `/vault/secrets/config` as a UTF-8 JSON object.
The path is fixed; the former `VAULT_CONFIG_FILE` environment variable is no
longer used. The application does not connect to Vault, authenticate, handle
tokens, or call Vault APIs. A separate deployment repository is responsible for
rendering and mounting the file; no deployment resources are configured here.

Example file using the application's existing configuration key:

```json
{
  "APP_ENV": "development"
}
```

Use a plain JSON object, without a Vault API response envelope, shell `export`
statements, or `KEY=value` syntax. JSON escaping must be applied when rendering
values. The runtime user (`appuser` in the Docker image) must be able to read the
file. The application only reads it and never writes it. Render updates
atomically so readers cannot observe partial JSON.

## Keys and behavior

There are **no required secret keys** in the current application. `APP_ENV` is
the only file key consumed by business logic, and it is optional. When present,
it must be a non-empty JSON string. It is returned publicly as `environment`
by `/api/info`, so it must not contain credentials. An empty object (`{}`) is
valid. Other file keys are not used or returned by the application.
`DEMO_API_KEY` appeared only in the previous loader test; the application does
not consume or require it.

Existing fallback behavior is preserved:

- If the file is missing, `/api/info` uses the `APP_ENV` environment variable,
  defaulting to `development`. Readiness remains successful because there are
  no required secrets.
- If the file exists without `APP_ENV`, `/api/info` uses the `APP_ENV`
  environment variable, defaulting to `local`.
- `/` continues to use the `APP_ENV` environment variable, defaulting to `local`.
- `APP_VERSION` remains an environment variable, defaulting to `dev`; it is
  not read from the file.

The loader reads the file on each `/api/info` and `/health/ready` request, so
changes are picked up without a restart. Unreadable files, malformed JSON,
non-object JSON, invalid UTF-8, and invalid `APP_ENV` values cause those endpoints
to return HTTP 503 with a generic error. File contents and parser diagnostics
are not included in responses or logged. `/health/live` stays independent of
configuration validity.

The existing `/api/info` response key `vault_config_loaded` is retained for API
compatibility. It indicates whether the mounted configuration file is present
after successful loading; it does not indicate a Vault connection.

Keep real runtime secret files outside the source tree and Docker build context.
Do not commit them or log their contents. The Dockerfile copies only application
code and dependency specifications; the runtime file must be mounted separately.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
