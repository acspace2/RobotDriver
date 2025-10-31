RobotDriver — Login → Search → Report Price (+ MCP, API)

Playwright-based e-commerce automation demo.

Core: Login → search a product → extract price

MCP Server: Execute LLM-generated JSON plans (/mcp/*)

Mini API: Query price over HTTP (/price, /price/quick)

The repository ships with a site adapter for automationexercise.com.
To support another site, implement a new adapter and swap it in.

Project Layout
RobotDriver/
  Main.py                     # CLI: Login → Search → Price
  ApiServer.py                # FastAPI: /health, /price, /price/quick
  MCPServer.py                # FastAPI: /mcp/describe_page, /mcp/execute_plan
  Core/
    Session.py                # Playwright BrowserSession context manager
  Service/
    Login.py                  # AuthService (login + optional sign-up)
    ProductPrice.py           # CatalogService (search → price extraction)
  Site/
    Base.py                   # SiteAdapter interface (strategy pattern)
    AutomationExercise.py     # automationexercise.com adapter
  Util/
    Parsing.py                # Price text parser
requirements.txt
README.md

Requirements

Python 3.10+ (3.12 recommended)

One-time browser install: python -m playwright install

Dependencies: pip install -r requirements.txt

requirements.txt (minimal)

playwright>=1.46
fastapi>=0.110
uvicorn>=0.29
pydantic>=2.6

Install

Windows (PowerShell)

py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install


Windows (CMD)

py -3 -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m playwright install


macOS / Linux (bash/zsh)

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install

Run (Core / CLI)

Existing account

python -m RobotDriver.Main --email "you@example.com" --password "yourpass" -p "Blue Top" --headful


No account? Auto sign-up then proceed

python -m RobotDriver.Main --email "unique_123@example.com" --password "MyPass!123" \
  -p "Blue Top" --signup-if-needed --headful


Exit codes

0 : success (product found and price extracted)

2 : logical failure (login failed / product not found / price missing)

On Windows, continuation characters differ by shell. To avoid confusion, prefer single-line commands.

Run (Mini API)
uvicorn RobotDriver.ApiServer:app --host 0.0.0.0 --port 8000


Health

curl http://127.0.0.1:8000/health


Price

curl -X POST http://127.0.0.1:8000/price -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpass","product":"Blue Top"}'


Quick demo (uses env vars)

PowerShell

$env:AE_EMAIL="you@example.com"
$env:AE_PASSWORD="yourpass"
curl "http://127.0.0.1:8000/price/quick?product=Blue%20Top"


CMD

set AE_EMAIL=you@example.com
set AE_PASSWORD=yourpass
curl "http://127.0.0.1:8000/price/quick?product=Blue%20Top"


macOS/Linux

export AE_EMAIL=you@example.com
export AE_PASSWORD=yourpass
curl "http://127.0.0.1:8000/price/quick?product=Blue%20Top"

Run (MCP)
uvicorn RobotDriver.MCPServer:app --host 0.0.0.0 --port 8001


Describe

curl "http://127.0.0.1:8001/mcp/describe_page?url=https://automationexercise.com/products&depth=2"


Execute plan

curl -X POST http://127.0.0.1:8001/mcp/execute_plan \
  -H "Content-Type: application/json" -d @plan.json


plan.json example:

{
  "headless": true,
  "steps": [
    {"action":"goto","url":"https://automationexercise.com/login"},
    {"action":"fill","role":"textbox","name":"Email Address","text":"you@example.com"},
    {"action":"fill","role":"textbox","name":"Password","text":"yourpass"},
    {"action":"click","selector":"button[data-qa='login-button']"},
    {"action":"goto","url":"https://automationexercise.com/products"},
    {"action":"fill","selector":"#search_product","text":"Blue Top"},
    {"action":"click","selector":"#submit_search"},
    {"action":"wait_for","selector":".features_items"},
    {"action":"click","selector":".productinfo.text-center:has-text('Blue Top') a:has-text('View Product')"},
    {"action":"wait_for","selector":".product-information"},
    {"action":"read_text","selector":".product-information span.price"}
  ]
}


Supported actions: goto | click | fill | wait_for | wait_url | read_text | screenshot

How It Works

BrowserSession (Core/Session.py) — Context manager that opens Chromium, creates a fresh context/page, applies default timeouts, and guarantees cleanup.

SiteAdapter (Site/Base.py) — Strategy interface that encapsulates site-specific selectors/flows. AutomationExerciseAdapter implements login/sign-up/search/price.

AuthService / CatalogService — Site-agnostic services delegating to the adapter, making logic reusable and easy to test.

Troubleshooting

ModuleNotFoundError: RobotDriver → Run from the project root using module mode:
python -m RobotDriver.Main ...

Playwright browsers missing → python -m playwright install

Slow network / timeouts → Increase default timeouts in Core/Session.py or add explicit wait_for_* in the adapter.

Anti-bot / 2FA → This demo targets a test site. Real sites may block automation.

Security Notes

Do not commit real credentials.

For demos, use AE_EMAIL / AE_PASSWORD environment variables.

License

MIT

Requirement Mapping

Required Core

Browser automation with Playwright (go/click/fill/wait)

Error handling & clear final result on CLI

Exit with explicit success/failure codes

Optional 1 (MCP)

Accessibility snapshot endpoint (/mcp/describe_page)

JSON plan executor (/mcp/execute_plan) with per-step logs

Prefers role+name targeting; selectors as fallback

Optional 2 (Shareable API)

FastAPI /price endpoint (+ /price/quick)

This README includes setup & run instructions