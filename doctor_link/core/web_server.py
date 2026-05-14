from __future__ import annotations

import functools
import shutil
import socket
import webbrowser
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from doctor_link.core.reports_indexer import index_reports
from doctor_link.core.web_detail_renderer import write_package_detail_html
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.web_renderer import write_reports_index_html


@dataclass
class WebViewResult:
    package_dir: str
    output_dir: str
    index_path: str
    url: str


def build_web_view(package_dir: Path, output_dir: Path | None = None) -> WebViewResult:
    """Build static assets for a package or reports-root web view without starting a server."""
    package_dir = package_dir.resolve()
    if _is_reports_root(package_dir):
        return build_reports_index_view(package_dir, output_dir)

    output_dir = (output_dir or package_dir / ".doctorlink-web").resolve()
    view = read_package_view(package_dir)
    index_path = write_package_detail_html(view, output_dir / "index.html")
    return WebViewResult(
        package_dir=str(package_dir),
        output_dir=str(output_dir),
        index_path=str(index_path),
        url="",
    )


def build_reports_index_view(reports_root: Path, output_dir: Path | None = None) -> WebViewResult:
    """Build a local workbench index for a DoctorReports directory."""
    reports_root = reports_root.resolve()
    output_dir = (output_dir or reports_root / ".doctorlink-web").resolve()
    _reset_output_dir(output_dir)
    index = index_reports(reports_root)
    index_path = write_reports_index_html(index, output_dir / "index.html")
    for package in index.packages:
        package_dir = Path(package.path)
        view = read_package_view(package_dir)
        detail_dir = output_dir / "packages" / package.relative_path
        write_package_detail_html(view, detail_dir / "index.html")
    return WebViewResult(
        package_dir=str(reports_root),
        output_dir=str(output_dir),
        index_path=str(index_path),
        url="",
    )


def serve_web_view(
    package_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> WebViewResult:
    """Build and serve a local read-only web view.

    The server serves only the generated static view directory. It does not
    expose the whole diagnostic package directory.
    """
    built = build_web_view(package_dir)
    output_dir = Path(built.output_dir)
    selected_port = _available_port(host, port)
    url = f"http://{host}:{selected_port}/index.html"

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(output_dir))
    server = ThreadingHTTPServer((host, selected_port), handler)

    if open_browser:
        webbrowser.open(url)

    try:
        print(f"Doctor link web view: {url}")
        print("Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    return WebViewResult(
        package_dir=built.package_dir,
        output_dir=built.output_dir,
        index_path=built.index_path,
        url=url,
    )


def _is_reports_root(path: Path) -> bool:
    if (path / "doctor-report.json").is_file():
        return False
    return any((item / "doctor-report.json").is_file() for item in path.iterdir() if item.is_dir())


def _reset_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def _available_port(host: str, preferred_port: int) -> int:
    if preferred_port == 0:
        return _bind_ephemeral(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, preferred_port))
            return preferred_port
        except OSError:
            return _bind_ephemeral(host)


def _bind_ephemeral(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])
