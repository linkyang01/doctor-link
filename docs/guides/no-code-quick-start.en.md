# Doctor link No-code Quick Start (English)

Doctor link helps you collect evidence about a software problem and give a clear repair package to an AI coding tool or developer.

You do not need to write code. Copy and paste the commands below.

## What Doctor link creates

- A **diagnostic package** folder with reports, evidence, and next steps.
- An optional **HTML report** you can open in your browser.
- An optional **AI handoff folder** you can give to Cursor or another AI tool.

## Step 1 — Install

```bash
python3 --version
pip install -e .
doctor-link --version
```

You need Python 3.10 or newer.

## Step 2 — Run the wizard

```bash
doctor-link wizard
```

The wizard asks:

1. Which folder to inspect
2. What problem you see
3. Whether to collect logs automatically
4. Whether to create an AI handoff package

At the end it prints exactly what to open or share next.

## Step 3 — Or use one command

```bash
doctor-link diagnose-now /path/to/your/project --full --summary "short problem description"
```

Add `--handoff` if you want the AI package immediately:

```bash
doctor-link diagnose-now /path/to/your/project --full --handoff --summary "login fails"
```

## Step 4 — Open your results

```bash
doctor-link home --reports DoctorReports
```

Open the printed `index.html` file in your browser.

## What to send to AI

Send the **handoff folder** printed by `wizard` or `diagnose-now --handoff`.

Do not send:

- unrelated personal files;
- production secrets;
- full disk backups.

## If a command fails

| Problem | What to do |
|---------|------------|
| Folder not found | Check the path and try again |
| Python too old | Install Python 3.10+ |
| No package found | Run `doctor-link report .` first |
| Permission denied | Choose a folder you can write to |

## Next step for developers

See `docs/quick-start.md` for the full CLI workflow.