# cursor_augmented_engineering

Sample pipeline repository for the **AI-Augmented Engineering for Data Engineers** course.

> This repository is for course delivery only. Do not use in production.

---

## What This Is

A three-stage market data pipeline in Perl (legacy) and Python (conversion target),
used across four hands-on labs to practise AI-augmented engineering with Cursor and GitHub Copilot Enterprise.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
pytest tests/ -v
```

All tests use mock fixtures. No API keys or external connections required.

## Repository Structure

```
perl/           Perl source -- three-stage market data pipeline
src/            Python source -- idiomatic conversions of each Perl module
tests/          pytest test suites for all Python modules
data/           Sample market data CSV + pre-computed Perl reference output
docs/           Pipeline map and conversion plan (generated during labs)
logs/           Sample Airflow failure logs (Lab 4)
metrics/        Pipeline quality metrics JSON (Lab 4)
schemas/        Expected schema definition (Lab 4)
audit/          Agent decision audit log (Lab 4)
.cursor/        Cursor rules, skills, and Bugbot configuration
lab-starters/   Starter files for each lab (Cursor path)
copilot-starters/ Starter files for each lab (Copilot path)
instructor-notes/ PR branch specification and instructor reference
AGENTS.md       Cloud Agent onboarding guide
```

## Perl Prerequisites

```bash
# Debian/Ubuntu
sudo apt-get install perl libwww-perl libjson-perl

# macOS
brew install perl
cpan LWP::UserAgent JSON
```

## The Engineered Regression

All five exchange codes (US, GB, DE, FR, JP) each appear in exactly 4 of the 20 sample records.
With all counts tied, Perl's `reverse sort` and Python's `sorted(..., reverse=True)` produce different orderings.
All 20 output records differ in the `exchange_rank` column.
Tests pass. The parity check catches it.
