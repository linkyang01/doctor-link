from __future__ import annotations

from pathlib import Path

from doctor_link.core.config_loader import load_config, merge_collect_cli, merge_package_cli, merge_verify_cli


def test_load_config_reads_doctorlink_files(tmp_path: Path) -> None:
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "collect.yml").write_text(
        """
collect:
  project_root: .
  logs:
    - logs/*.log
  commands:
    - python --version
  redaction:
    enabled: true
    email: true
    phone: false
    patterns:
      - internal-[0-9]+
""".strip(),
        encoding="utf-8",
    )
    (config_dir / "package.yml").write_text(
        """
package:
  output_dir: DoctorReports
  exclude_logs: true
  max_file_size: 123
""".strip(),
        encoding="utf-8",
    )
    (config_dir / "verification.yml").write_text(
        """
verification:
  write_back: true
  required_signals:
    - test_records
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config.root_dir == str(tmp_path)
    assert config.collect.logs == ["logs/*.log"]
    assert config.collect.commands == ["python --version"]
    assert config.collect.redact_email is True
    assert config.collect.redact_patterns == ["internal-[0-9]+"]
    assert config.package.exclude_logs is True
    assert config.package.max_file_size == 123
    assert config.verification.write_back is True
    assert config.verification.required_signals == ["test_records"]


def test_load_config_falls_back_to_defaults_without_files(tmp_path: Path) -> None:
    config = load_config(tmp_path)

    assert config.root_dir == str(tmp_path.resolve())
    assert config.collect.logs == []
    assert config.package.output_dir == "DoctorReports"
    assert "Missing config file" in "\n".join(config.warnings)


def test_merge_collect_cli_prefers_explicit_values(tmp_path: Path) -> None:
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "collect.yml").write_text(
        """
collect:
  project_root: config-root
  logs:
    - config.log
  commands:
    - config-command
  redaction:
    enabled: true
    email: false
""".strip(),
        encoding="utf-8",
    )
    config = load_config(tmp_path)

    merged = merge_collect_cli(
        config.collect,
        project_root=tmp_path,
        log_patterns=["cli.log"],
        commands=["cli-command"],
        no_redact=True,
        redact_email=True,
        custom_patterns=["CUSTOM"],
    )

    assert merged.project_root == str(tmp_path)
    assert merged.logs == ["cli.log"]
    assert merged.commands == ["cli-command"]
    assert merged.redact is False
    assert merged.redact_email is True
    assert merged.redact_patterns == ["CUSTOM"]


def test_merge_package_and_verify_cli() -> None:
    package = merge_package_cli(
        load_config(Path.cwd()).package,
        output=Path("out/package.zip"),
        exclude_attachments=True,
        max_file_size=5,
    )
    assert package.output_dir == "out"
    assert package.exclude_attachments is True
    assert package.max_file_size == 5

    verify = merge_verify_cli(load_config(Path.cwd()).verification, write_back=True)
    assert verify.write_back is True
