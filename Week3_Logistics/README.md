# Week 3 — Advanced Logistics Data Analysis and Visualization

**All data and findings are simulated.** This is NEW Week 3 code, not your Week 2 scripts. No original dataset download is needed.

## Run in VS Code (Windows)
1. Extract the ZIP completely. Do not run files inside the compressed ZIP.
2. In VS Code, choose File > Open Folder > the extracted `Week3_Logistics` folder.
3. Choose Terminal > New Terminal.
4. Run:
```powershell
cmd /c RUN_WEEK3.bat
```
If the terminal is not in this folder, first run `cd "YOUR ACTUAL EXTRACTED FOLDER PATH"`. Do not paste that placeholder unchanged.

Alternatively double-click RUN_WEEK3.bat in the extracted folder. The window pauses on both success and failure. First installation requires internet and can take several minutes.

## Requirements
64-bit Python 3.11 or newer (recommended 3.11–3.14). Your previously checked laptop had Python 3.14. The libraries are pinned to the versions used to verify this package. If package installation fails, send the actual terminal error; do not skip the tests.

## What runs automatically
1. Creates `.venv` in this folder and installs dependencies.
2. Runs 15 tests (must end in OK).
3. Runs `run_week3.py`, which generates 3,000 shipments with seed 2026, validates them, and exports EDA tables and eight charts.

You do NOT need to execute `simulation.py` and `analysis.py` separately. They are imported by the runner.

## Manual commands (if preferred)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe run_week3.py
```
For macOS/Linux use `python3 -m venv .venv`, then `.venv/bin/python` in place of the Windows executable.

## Files
- `Week3_Logistics_Report.docx`: supplied Word report, charts and verified default-seed interpretations. The runner does not rebuild Word.
- `simulation.py`: dataset generator and quality-validation rules.
- `analysis.py`: descriptive EDA, grouped metrics, correlations and charts.
- `run_week3.py`: single pipeline entry point.
- `tests/test_week3.py`: reproducibility, validation and hand-calculated aggregation tests.
- `data/simulated_shipments.csv`: 3,000 rows × 19 columns, one row per shipment.
- `data/simulation_assumptions.json`: complete assumptions, seed and hypothetical INR rates.
- `results/figures/`: eight PNG figures.
- `results/`: descriptive statistics, monthly/service/region summaries, Pearson and Spearman matrices, cost-component table, metrics.json, environment versions, checksum and package-build test log.

The included test log records the package verification, not execution on your laptop. Save your own terminal screenshot showing tests and SUCCESS after running locally.

## Interpretation safeguards
- Transportation-cost rates and service promises are invented assumptions, not real tariffs.
- Increased monthly demand, East-region dwell, and speed/cost differences are programmed. They do not prove actual seasonality or real bottlenecks.
- Express is faster on average but has a stricter promised deadline; on-time rates and delivery speeds answer different questions.
- Distance/cost correlation partly follows directly from the cost formula; it is not an independent validation of real cost drivers.
- Tails are retained because simulated records pass quality checks. IQR counts overlap across columns; do not sum them as unique shipments.
- Every shipment eventually delivers in this scenario. June dispatches may deliver in early July; analysis is grouped by dispatch month.
- Tables use all shipments; cost/unit is total cost divided by total units, not mean individual cost/unit.
- Changing seed or formulas changes findings. The supplied report matches the default code only.

## Submission checklist
- Read the report, confirm your identifying details, and understand every chart.
- Run the launcher and save genuine execution evidence.
- Submit the DOCX and scripts through the required internship portal/repository method.
- Keep data, figures, tests and requirements available for reproduction.
- Do not claim these are company records. No score is guaranteed.
- Add a personal reflection only if it describes your actual work and understanding.
