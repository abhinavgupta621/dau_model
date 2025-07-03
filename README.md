📈 DAU Scenario Dashboard

Upload your DAU model.xlsx, tweak installs/retention/engagement with sliders, and watch scenarios update live in an interactive Plotly chart—all from your browser.

<p align="center">
  <!-- Replace with actual GIF after recording -->
  <img src="docs/demo.gif" alt="DAU Scenario Dashboard demo" width="720">
</p>



⸻

✨ Features
	•	Plug-and-play upload – point to any workbook that uses the same Basedata and DAU_Model_imapct sheets.
	•	Scenario sliders – scale installs, adjust retention ±25 %, or nudge engagement and see instant recalcs.
	•	Drag-sort metric picker – choose up to four KPIs and reorder them on the fly.
	•	Beautiful charts – Plotly line chart with unified hover, export buttons, dark-mode aware.
	•	Data explorer – expandable raw-data table with download-as-CSV.
	•	Lightweight codebase – 250 LOC Streamlit + pandas + plotly (no heavy BI stack).

⸻

🚀 Quick start

# 1. Clone the repo & cd
$ git clone https://github.com/your-org/dau-scenario-dashboard.git
$ cd dau-scenario-dashboard

# 2. Create a virtual env (optional)
$ python -m venv .venv && source .venv/bin/activate

# 3. Install deps
$ pip install -r requirements.txt

# 4. Run the app
$ streamlit run dau_dashboard.py

Open your browser to http://localhost:8501 and upload DAU model.xlsx.

Requirements
	•	Python ≥3.9
	•	Packages: streamlit, pandas, openpyxl, plotly (see requirements.txt)

⸻

🖼️ Screenshots

Sidebar & chart	Metric drag-sort	Raw data expander
		


⸻

🛠 How it works
	1.	Upload – Excel is parsed with openpyxl; the two sheets are cached in session state.
	2.	Re-calc – recalc_df() applies multipliers/deltas to installs, retention and engagement, then re-computes a minimal set of “*_calc” columns for speed.
	3.	Visualize – Data is melted long-form and sent to Plotly for a multi-series line chart.
	4.	Interact – Streamlit widgets store driver tweaks and metric order in session state so UI stays reactive.

See detailed inline docs in dau_dashboard.py.

⸻

🗺️ Roadmap
	•	Full parity with every Excel formula (cohort waterfall).
	•	Cohort retention heatmap.
	•	Dockerfile + Render/Heroku one-click deploy.
	•	Theme toggle & metric color palettes.

Have an idea? Open an issue or start a PR!

⸻

🤝 Contributing
	1.	Fork the project and create your feature branch (git checkout -b feat/amazing-feature).
	2.	Commit your changes (git commit -m 'Add amazing feature').
	3.	Push to the branch (git push origin feat/amazing-feature).
	4.	Open a pull request.

This repo uses pre-commit to run black, ruff and isort. Install hooks with:

pre-commit install


⸻

📄 License

Distributed under the MIT License.

⸻

🙌 Acknowledgements
	•	Inspired by the original DAU_Model.xlsx spreadsheet (internal analytics team).
	•	Built with Streamlit and Plotly.
