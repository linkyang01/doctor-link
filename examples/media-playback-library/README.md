# Media Playback Library Example

A Vly-style media sample library for Doctor link Core Proof walkthroughs.

## Scenario

Validate whether a playback test library has the minimum media categories before asking AI to diagnose playback failures.

## Layout

```text
examples/media-playback-library/
├── README.md
├── samples/
│   ├── basic/sample.mp4
│   ├── complex/sample.mkv
│   ├── subtitles/sample.srt
│   └── audio/sample.flac
└── .doctorlink/
    └── diagnosis.yml
```

## Walkthrough

```bash
doctor-link report examples/media-playback-library --out /tmp/media-reports
doctor-link vly-proof examples/media-playback-library --package-dir <package-from-report>
doctor-link verify <package-from-report>
doctor-link view <package-from-report> --build-only
```

Expected result: Vly Core Proof status `GO` because required sample categories are present.