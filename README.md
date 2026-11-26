<div align="center">

# Direct Debit Dashboard (PS2)

### Financial ETL Pipeline and Reactive Analytics Platform for Legacy Banking Files

> A modular Python analytics application that parses, validates, and visualizes monthly direct debit batches in the fixed-width **PS2** banking format — transforming raw legacy transmissions into an interactive financial dashboard powered by **Shiny for Python**, **Pandas**, and **Plotly**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Shiny for Python](https://img.shields.io/badge/Shiny_for_Python-v1.0%2B-447099?style=flat-square&logo=posit&logoColor=white)](https://shiny.posit.co/py/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.0%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![UPCA](https://img.shields.io/badge/UPCA-LESI-009639?style=flat-square)](https://www.ipca.pt/)
[![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)](https://github.com/IPCALESI2526/d-43)

</div>

---

## Academic Context

| | |
|---|---|
| **Institution** | Polytechnic University of Cávado and Ave (UPCA) |
| **Degree** | B.Sc. in Computer Systems Engineering (*Daytime Program*) |
| **Course** | Computer Science Laboratories (2025/2026) |
| **Deliverables** | Python ETL Parser, Reactive Web Dashboard, Doxygen Docs, and LaTeX Technical Report |

---

## Table of Contents

- [Overview](#overview)
- [The Problem and Solution](#the-problem-and-solution)
- [Key Features](#key-features)
- [System Architecture and Data Pipeline](#system-architecture-and-data-pipeline)
- [Engineering Decisions](#engineering-decisions)
- [PS2 Format Specification](#ps2-format-specification)
- [Demo](#demo)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Installation and Usage](#installation-and-usage)
- [Technical Documentation](#technical-documentation)
- [Development Team (Group 43)](#development-team-group-43)
- [References](#references)

---

## Overview

The **Direct Debit Dashboard (PS2)** is an end-to-end data processing and visualization application built to ingest, normalize, audit, and analyze monthly direct debit bank batches formatted under the legacy Portuguese **PS2** specification (modeled around the billing entity *IPCA Energy*).

Rather than inspecting raw fixed-width text files manually, finance operators gain a reactive web interface built with **Shiny for Python**. The application decouples low-level positional file parsing from interactive UI rendering, delivering real-time executive KPIs, time-series revenue tracking, customer spend rankings, and searchable transaction ledgers.

---

## The Problem and Solution

Legacy banking interchange formats such as **PS2** rely on dense, fixed-width ASCII lines without delimiters or headers. Auditing these transmissions manually creates three major operational bottlenecks:

| Challenge | Application Solution |
|---|---|
| **Unreadable positional data** with packed numeric fields and implicit decimals | Automated fixed-width ETL parser (`src/parser.py`) that slices fields deterministically and converts integer cents into euro values |
| **Concatenated customer identifiers** combining tax and banking codes into a single 30-character string | Strict field extraction into validated 9-digit **NIF** (Tax ID) and 21-digit **NIB** (Bank Account) columns with readable display formatting |
| **Limited financial visibility** across multiple monthly batch files | Multi-file ingestion into a unified Pandas DataFrame powering reactive date/customer filters, KPI cards, and interactive Plotly charts |

---

## Key Features

### Automated PS2 ETL & Data Normalization
- **Positional Record Parsing:** Reads and classifies header (`Type 1`), transaction (`Type 2`), and control footer (`Type 9`) records across monthly batch files in `data/`.
- **Identifier Decomposition:** Splits the raw 30-character customer block into a **9-digit NIF** and a **21-digit NIB** with whitespace formatting for scannable auditing.
- **Monetary Conversion:** Transforms zero-padded integer cent fields into precise decimal euro amounts.
- **Temporal Resolution & Consistency:** Extracts batch dates from file metadata/headers and cross-checks batch totals and record counts against header and footer control records.

### Interactive Reactive Dashboard
- **Dynamic Filtering:** Filter transactions instantaneously by custom date ranges and specific customer bank accounts (NIB) without page reloads.
- **Executive KPIs:** Live summary metrics displaying cumulative debit volume (EUR) and total processed transaction count for the active filter slice.
- **Time-Series Evolution Chart:** Interactive Plotly line chart tracking monthly direct debit totals over time with data markers and localized currency tooltips.
- **Top Customers by Spend:** Ranked horizontal/vertical bar chart highlighting the highest-billing customer accounts in the selected period.
- **Auditable Transaction Grid:** Chronologically ordered, paginated data table displaying formatted NIFs, NIBs, debit descriptions, dates, and euro amounts.

---

## System Architecture and Data Pipeline

The application follows a decoupled, two-stage architecture separating data ingestion (`parser.py`) from reactive presentation (`app.py`):

```text
╔══════════════════════════════════════════════════════════════════╗
║                  DATA SOURCE — Raw Banking Files                 ║
║               data/DD_YYYY_MM.ps2 (Fixed-Width PS2)              ║
║       Type 1 (Header) · Type 2 (Transaction) · Type 9 (Footer)   ║
╚════════════════════════════════╤═════════════════════════════════╝
                                 │  File I/O & Positional Slicing
╔════════════════════════════════▼═════════════════════════════════╗
║                   ETL LAYER — src/parser.py                      ║
║                                                                  ║
║  • Fixed-width field extraction     • NIF (9) / NIB (21) split   ║
║  • Integer cents → EUR conversion   • Header/Footer validation   ║
╚════════════════════════════════╤═════════════════════════════════╝
                                 │  Structured Pandas DataFrame
╔════════════════════════════════▼═════════════════════════════════╗
║            PRESENTATION LAYER — src/app.py (Shiny)               ║
║                                                                  ║
║  Reactive Inputs:   Date Range Filter · Customer (NIB) Selector  ║
║  Reactive Outputs:  KPI Cards · Plotly Time-Series & Top-Spend   ║
║                     Charts · Paginated Transaction Ledger        ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Engineering Decisions

Key architectural and workflow choices made during development:

| Decision | Rationale |
|---|---|
| **Separation of ETL (`parser.py`) and UI (`app.py`)** | Keeps parsing logic independent of the web framework, enabling isolated maintenance, easier debugging, and clean Doxygen API documentation |
| **Pandas as the in-memory analytics engine** | Vectorized filtering, grouping, and aggregation keep dashboard interactions responsive even when combining multiple monthly batches |
| **Shiny for Python reactive graph** | Automatically tracks dependencies between filter inputs and chart/table outputs, recalculating only affected components on user interaction |
| **Plotly Express for visualizations** | Delivers native zoom, pan, hover inspection, and PNG export out of the box—superior to static images for financial auditing |
| **Makefile task automation** | Standardizes environment setup, application startup, and workspace cleanup into reproducible single-word commands |
| **Automated code & academic documentation** | Pairs Doxygen-generated code reference (`ref/`) with a modular LaTeX technical report (`doc/`) for full project traceability |

---

## PS2 Format Specification

Files stored in `data/` represent monthly direct debit batches structured as fixed-width positional records:

| Record Type | Position | Field | Description |
| :---: | :---: | :--- | :--- |
| **1 (Header)** | `01-09` | Internal Date | File creation date (`YYYYMMDD`) |
| | `10-52` | Creditor Name | Name of the billing entity (e.g., `IPCA Energy`) |
| | `53-62` | Entity Tax ID (NIF) | Tax identification number of the creditor entity |
| | `63-75` | Total Amount | Cumulative batch amount (in cents) |
| | `76-81` | Record Count | Total number of transactions in the batch |
| **2 (Transaction)** | `09-11` | Sequence ID | Sequential record number within the batch |
| | `12-20` | Customer NIF | First 9 characters of the customer identifier field |
| | `21-41` | Customer NIB | Remaining 21 characters of the customer identifier field |
| | `42-55` | Amount | Debit amount (in cents) |
| | `56-82` | Description | Debit reference/reason (e.g., `Fatura Eletricidade 07/2025`) |
| **9 (Footer)** | `02-15` | Total Amount | Batch verification checksum total (in cents) |
| | `16-21` | Record Count | Final transaction count for batch auditing |

### Sample File (`DD_2025_07.ps2`)

```text
120250726IPCA Energy                                50123456700000000028779000010
2000000100100350651000025874125423568914200000000002136Fatura Eletricidade 07/2025
2000000100200330000452108745961550184592300000000004561Fatura Eletricidade 07/2025
2000000100300100000123456789012312345678900000000002063Fatura Eletricidade 07/2025
2000000100400360010234567890123429845123600000000002860Fatura Eletricidade 07/2025
2000000100500230099887766554433245678912300000000004507Fatura Eletricidade 07/2025
2000000100600380011223344556677887451236900000000002208Fatura Eletricidade 07/2025
2000000100700190055667788990011215975348600000000002208Fatura Eletricidade 07/2025
2000000100800420066554433221100995175325800000000002661Fatura Eletricidade 07/2025
2000000100900330012312312312312375315984200000000003077Fatura Eletricidade 07/2025
2000000101000110099880077665544362839415700000000002498Fatura Eletricidade 07/2025
900000000028779000010
```

---

## Demo

<div align="center">
  <img src="./assets/img/DashboardDebitos.png" alt="Direct Debit Dashboard Interface" width="95%">
  <p><em>Figure: Interactive Shiny for Python dashboard displaying dynamic date and NIB filters, KPI cards, Plotly analytics, and the formatted transaction ledger.</em></p>
</div>

---

## Repository Structure

```text
d-43/
├── assets/
│   └── img/
│       └── DashboardDebitos.png   # Dashboard screenshots and visual assets
├── data/                          # Input data (monthly batches in PS2 format)
│   ├── DD_2025_01.ps2
│   └── ...
├── doc/                           # Academic documentation and LaTeX report
│   ├── capas/
│   │   └── capa.tex
│   ├── capitulos/
│   │   ├── 01_introducao.tex
│   │   ├── 02_desenvolvimento.tex
│   │   └── 03_conclusao.tex
│   ├── d43-main.pdf               # Compiled final technical report
│   └── d43-main.tex               # Main LaTeX entry file
├── ref/                           # Technical code reference generated by Doxygen
│   ├── Doxyfile                   # Doxygen configuration file
│   ├── html/                      # HTML documentation output
│   └── latex/                     # LaTeX documentation output
├── src/                           # Application source code
│   ├── app.py                     # Reactive web application and dashboard (Shiny)
│   └── parser.py                  # PS2 file ingestion and parsing module
├── .gitignore                     # Git ignore rules
├── Makefile                       # Workflow automation (install, run, clean)
├── planeamento.md                 # Weekly planning, branches, and task allocation
├── README.md                      # Main repository documentation
└── requirements.txt               # Python project dependencies
```

---

## Tech Stack

| Technology | Version / Scope | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.10+ | Core language for ETL processing and web runtime |
| **Shiny for Python** | 1.0+ | Reactive web application framework |
| **Pandas** | 2.0+ | Tabular ingestion, cleaning, filtering, and aggregation |
| **Plotly Express** | 5.0+ | Interactive financial charts and tooltips |
| **LaTeX / BibLaTeX** | — | Structured academic and technical report authoring |
| **Doxygen** | — | Automated source-code API documentation |
| **Make** | — | Reproducible dependency installation and execution |

---

## Installation and Usage

### Prerequisites

- Python 3.10 or higher
- `pip` package manager
- `make` (optional, for automated workflow targets)

### 1. Clone the Repository

```bash
git clone [https://github.com/IPCALESI2526/d-43.git](https://github.com/IPCALESI2526/d-43.git)
cd d-43
```

### 2. Create and Activate a Virtual Environment (Recommended)

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Using the `Makefile`:

```bash
make install
```

Or directly via `pip`:

```bash
pip install -r requirements.txt
```

### 4. Start the Application

Using the `Makefile`:

```bash
make run
```

Or directly with the Shiny CLI:

```bash
shiny run src/app.py
```

Open the application in your browser at the local address printed in the terminal (typically `http://127.0.0.1:8000`).

---

## Technical Documentation

This repository includes two complementary documentation artifacts:

- **Source Code Reference (`ref/`):** Generated with **Doxygen** directly from docstrings in `src/parser.py` and `src/app.py`. Open `ref/html/index.html` in a browser to explore module, function, and parameter documentation.
- **Technical Report (`doc/`):** Full academic report authored in modular **LaTeX** (`doc/d43-main.tex`) and pre-compiled as `doc/d43-main.pdf`, covering system requirements, parser design, dashboard architecture, and conclusions.

---

## Development Team (Group 43)

| Planning Role | Student ID | Name |
| :---: | :---: | :--- |
| **A1** | `29330` | Edgar Brito |
| **A2** | `29328` | Tiago Lima |
| **A3** | `29333` | Rui Araújo |
| **A4** | `29325` | Henrique Ribeiro |

See [planeamento.md](./planeamento.md) for weekly sprint planning, branching strategy, commit history, and individual contributions.

---

## References

- [Shiny for Python Documentation](https://shiny.posit.co/py/)
- [Pandas User Guide](https://pandas.pydata.org/docs/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Doxygen Official Manual](https://www.doxygen.nl/manual/)
- [gitignore.io](https://www.toptal.com/developers/gitignore)
