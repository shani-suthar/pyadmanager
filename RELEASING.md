# Releasing

This guides commit message style and how to cut a release (a tagged version published to PyPI).

## Commit messages

Subject line: capitalized, imperative mood, no trailing period. Prefix with `Fix:` when the commit
is a bug fix; otherwise start directly with the verb (`Add`, `Refactor`, `Enhance`, `Remove`, ...).
Keep the subject short — put any further explanation in the body, separated by a blank line.

```
Add Programmatic Buyer, Role, User services and corresponding filters

Fix: Update README badges for accurate links and cache busting

Refactor tests to remove filter classes and directly use client methods for building filter strings
```

Body (optional): explain *why*, not what — the diff already shows what changed.

```
Rename resource client list_*/get_* methods to plain list()/get()

The resource is already implied by which client you call it on
(client.line_item.list() vs client.line_item.list_line_items()), so
the longer names were redundant. custom_targeting.py keeps its
list_keys/get_key/list_values/get_value naming since that one client
covers two distinct resources.
```

## Releasing a version

Releases are tag-driven: pushing a tag matching `v*.*.*` runs [`.github/workflows/release.yaml`](.github/workflows/release.yaml),
which re-runs code quality checks, verifies the tag matches `pyproject.toml`'s `version`, then builds
and publishes to PyPI via trusted publishing (no API token needed).

1. Bump `version` in [`pyproject.toml`](pyproject.toml) and commit it:

   ```bash
   git commit -am "Bump version to 0.2.0"
   ```

2. Push the commit, then tag it and push the tag. The tag must be `v` + the exact `pyproject.toml`
   version (`version_check` in the workflow fails the release otherwise):

   ```bash
   git push origin main
   git tag -a v0.2.0 -m "v0.2.0"
   git push origin v0.2.0
   ```

3. Watch the `Release to PyPI` run under the repo's Actions tab. On success the new version is live
   on PyPI.

### Example

Releasing `0.1.0` → `0.1.1`:

```bash
# pyproject.toml: version = "0.1.0" -> "0.1.1"
git commit -am "Bump version to 0.1.1"
git push origin main
git tag -a v0.1.1 -m "v0.1.1"
git push origin v0.1.1
```
