from pathlib import Path

# Restore known-good files before applying the patch. The backups were made
# immediately before this migration.
Path('/app/evoagent/github.py').write_text(Path('/tmp/github.py.before_pr_files').read_text())
Path('/app/evoagent/service.py').write_text(Path('/tmp/service.py.before_pr_files').read_text())

path = Path('/app/evoagent/github.py')
text = path.read_text()
old = '''    def fetch_diff(self, url: str) -> str:
        body = self._request(
            "GET", url, accept="application/vnd.github.v3.diff", raw=True
        )
        return body.decode("utf-8", errors="replace")

'''
new = r'''    def fetch_diff(self, url: str) -> str:
        body = self._request(
            "GET", url, accept="application/vnd.github.v3.diff", raw=True
        )
        return body.decode("utf-8", errors="replace")

    def fetch_pull_files_diff(self, repository: str, number: int) -> str:
        """Fetch a PR diff through the GitHub API instead of the web .diff URL.

        The webhook diff_url points at github.com/.../pull/N.diff, which is a
        web-rendered endpoint and can intermittently return Unicorn/503 pages.
        The pulls/{number}/files API is token-authenticated and returns stable,
        structured per-file patches.
        """
        files = []
        page = 1
        while True:
            url = (
                "https://api.github.com/repos/%s/pulls/%d/files?per_page=100&page=%d"
                % (repository, number, page)
            )
            batch = self._json("GET", url)
            if not batch:
                break
            files.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        chunks = []
        for item in files:
            filename = item.get("filename")
            patch = item.get("patch")
            if not filename or not patch:
                continue
            previous = item.get("previous_filename") or filename
            chunks.extend([
                "diff --git a/%s b/%s\n" % (previous, filename),
                "--- a/%s\n" % previous,
                "+++ b/%s\n" % filename,
                patch,
                "\n",
            ])
        return "".join(chunks)

'''
new = new.replace('\\"', '"').replace('\\n', '\\n')
if old not in text:
    raise SystemExit('fetch_diff block not found')
path.write_text(text.replace(old, new))

path = Path('/app/evoagent/service.py')
text = path.read_text()
old = '''            client.ensure_repository_access(payload["repository"])
            diff = client.fetch_diff(payload["diff_url"])
            self._validate_review(payload["repository"], diff)
'''
new = '''            client.ensure_repository_access(payload["repository"])
            if payload.get("pull_request"):
                try:
                    diff = client.fetch_pull_files_diff(
                        payload["repository"], int(payload["pull_request"])
                    )
                except Exception:
                    diff = client.fetch_diff(payload["diff_url"])
            else:
                diff = client.fetch_diff(payload["diff_url"])
            self._validate_review(payload["repository"], diff)
'''
if old not in text:
    raise SystemExit('service diff fetch block not found')
path.write_text(text.replace(old, new))
