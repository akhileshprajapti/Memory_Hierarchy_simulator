# MemoryLab – Memory Hierarchy Simulator

An interactive Computer Organization and Architecture mini project built with Python, Flask, HTML, CSS, JavaScript and Chart.js.

## Features
- Configurable L1, L2 and L3 cache levels
- Direct, fully associative and set-associative mapping
- LRU, FIFO and Random replacement policies
- Decimal and hexadecimal memory address input
- Cache hit/miss ratios, evictions, and average access latency
- Per-access execution trace
- Replacement-policy comparison
- Interactive charts

## Run on Windows
1. Install Python 3.10+ and Git.
2. Open this folder in VS Code.
3. In the terminal run:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

4. Open http://127.0.0.1:5000

If PowerShell blocks environment activation, run:
`Set-ExecutionPolicy -Scope Process Bypass`
Then activate again.

## Run on macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## How the simulator works
Addresses are byte addresses. The block number is `address // block_size`. Set index is `block_number % number_of_sets`; tag is `block_number // number_of_sets`. Cache levels are checked from L1 toward lower levels. A hit in a lower cache fills the missed upper levels; a main-memory access fills all enabled cache levels.

The reported hierarchy hit ratio counts an access as a hit if any enabled cache level satisfies it. Average access latency is calculated as the mean of accumulated cache lookup times plus the configured main-memory penalty on a complete miss. These are educational model assumptions, not real hardware benchmarks.

## GitHub
Create a public repository named `Memory-Hierarchy-Simulator`, then run:

```bash
git init
git add .
git commit -m "Initial MemoryLab project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Memory-Hierarchy-Simulator.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Deploy with Render
1. Push the project to GitHub.
2. Sign in at https://render.com/.
3. Select New → Web Service and connect the repository.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Deploy and open the generated Render URL.

The included Procfile contains `web: gunicorn app:app`.

## Formula
Single-level simplified AMAT:
`AMAT = Hit Time + (Miss Rate × Miss Penalty)`

For this multi-level model, the displayed average is the mean of accumulated lookup latency for the full sequence.

## License
MIT
