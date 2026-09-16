#!/usr/bin/env python3
"""Minimal zero-dependency static server for Noah's Blog.

The site is a pre-built Hexo blog whose pages reference assets with an
absolute ``/blog/`` URL prefix (e.g. ``/blog/css/style.css``). Serving the
repository root directly would 404 every asset, so this handler maps the
``/blog/`` prefix onto the repository root and redirects ``/`` to ``/blog/``.
"""

import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "/blog"


class BlogHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self._maybe_redirect_root():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._maybe_redirect_root():
            return
        super().do_HEAD()

    def _maybe_redirect_root(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("", "/"):
            self.send_response(302)
            self.send_header("Location", PREFIX + "/")
            self.end_headers()
            return True
        return False

    def translate_path(self, path):
        # Strip the /blog prefix before resolving against the repo root.
        query_split = path.split("?", 1)[0]
        if query_split == PREFIX:
            path = "/"
        elif query_split.startswith(PREFIX + "/"):
            path = path[len(PREFIX):]
        return super().translate_path(path)


def main():
    host = os.environ.get("BLOG_HOST", "0.0.0.0")
    port = int(os.environ.get("BLOG_PORT", "4000"))
    handler = partial(BlogHandler, directory=REPO_ROOT)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving Noah's Blog from {REPO_ROOT} at http://{host}:{port}{PREFIX}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down blog server")
        server.shutdown()


if __name__ == "__main__":
    main()
