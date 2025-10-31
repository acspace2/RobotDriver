<h2>RobotDriver — Login → Search → Report Price (+ MCP, API)</h2>

<b>Core</b>: Login → search a product → <b>extract price</b><br>

<b>MCP Server</b>: Execute <b>LLM-generated JSON plans</b> (<code>/mcp/*</code>)<br>

<b>Mini API</b>: Query price over HTTP (<code>/price</code>, <code>/price/quick</code>)<br>
Adapter for <b>automationexercise.com</b> is included; swap the adapter to target another site.

<h3>Project Layout</h3>

<code>RobotDriver/Main.py</code> — CLI: Login → Search → Price<br>

<code>RobotDriver/ApiServer.py</code> — FastAPI: <code>/health</code>, <code>/price</code>, <code>/price/quick</code><br>

<code>RobotDriver/MCPServer.py</code> — FastAPI: <code>/mcp/describe_page</code>, <code>/mcp/execute_plan</code><br>

<code>RobotDriver/Core/Session.py</code> — Playwright <i>BrowserSession</i><br>

<code>RobotDriver/Service/Login.py</code> — AuthService (login + optional sign-up)<br>

<code>RobotDriver/Service/ProductPrice.py</code> — CatalogService (search → price)<br>

<code>RobotDriver/Site/Base.py</code> — SiteAdapter interface (strategy)<br>

<code>RobotDriver/Site/AutomationExercise.py</code> — site adapter<br>

<code>RobotDriver/Util/Parsing.py</code> — price text parser<br>

<h3>Requirements</h3>

Python <b>3.10+</b> (3.12 recommended)<br>

One-time browser install: <code>python -m playwright install</code><br>

Deps: <code>pip install -r requirements.txt</code><br>

<h3>Install</h3>

<b>Windows (PowerShell)</b>

<pre><code>py -3 -m venv .venv . .\.venv\Scripts\Activate.ps1 pip install -r requirements.txt python -m playwright install </code></pre>

<b>Windows (CMD)</b>

<pre><code>py -3 -m venv .venv .\.venv\Scripts\activate.bat pip install -r requirements.txt python -m playwright install </code></pre>

<b>macOS / Linux</b>

<pre><code>python3 -m venv .venv source .venv/bin/activate pip install -r requirements.txt python -m playwright install </code></pre> <h3>Run (Core / CLI)</h3>

<b>Existing account</b>

<pre><code>python -m RobotDriver.Main --email "you@example.com" --password "yourpass" -p "Blue Top" --headful </code></pre>

<b>No account? Auto sign-up then proceed</b>

<pre><code>python -m RobotDriver.Main --email "unique_123@example.com" --password "MyPass!123" -p "Blue Top" --signup-if-needed --headful </code></pre>

<b>Exit codes</b>: <code>0</code> = success (found+priced), <code>2</code> = logical failure (login/product/price)

<h3>Run (Mini API)</h3>

<b>Start server</b>

<pre><code>uvicorn RobotDriver.ApiServer:app --host 0.0.0.0 --port 8000 </code></pre>

<b>Health</b>

<pre><code>curl http://127.0.0.1:8000/health </code></pre>

<b>Price</b>

<pre><code>curl -X POST http://127.0.0.1:8000/price -H "Content-Type: application/json" \ -d '{"email":"you@example.com","password":"yourpass","product":"Blue Top"}' </code></pre>

<b>Quick demo (env vars)</b><br>
PowerShell

<pre><code>$env:AE_EMAIL="you@example.com" $env:AE_PASSWORD="yourpass" curl "http://127.0.0.1:8000/price/quick?product=Blue%20Top" </code></pre>

CMD

<pre><code>set AE_EMAIL=you@example.com set AE_PASSWORD=yourpass curl "http://127.0.0.1:8000/price/quick?product=Blue%20Top" </code></pre>

macOS/Linux

<pre><code>export AE_EMAIL=you@example.com export AE_PASSWORD=yourpass curl "http://127.0.0.1:8000/price/quick?product=Blue%20Top" </code></pre> <h3>Run (MCP)</h3>

<b>Start server</b>

<pre><code>uvicorn RobotDriver.MCPServer:app --host 0.0.0.0 --port 8001 </code></pre>

<b>Describe</b>

<pre><code>curl "http://127.0.0.1:8001/mcp/describe_page?url=https://automationexercise.com/products&amp;depth=2" </code></pre>

<b>Execute plan</b>

<pre><code>curl -X POST http://127.0.0.1:8001/mcp/execute_plan \ -H "Content-Type: application/json" -d @plan.json </code></pre>

<b><i>plan.json</i> example</b>

<pre><code>{ "headless": true, "steps": [ {"action":"goto","url":"https://automationexercise.com/login"}, {"action":"fill","role":"textbox","name":"Email Address","text":"you@example.com"}, {"action":"fill","role":"textbox","name":"Password","text":"yourpass"}, {"action":"click","selector":"button[data-qa='login-button']"}, {"action":"goto","url":"https://automationexercise.com/products"}, {"action":"fill","selector":"#search_product","text":"Blue Top"}, {"action":"click","selector":"#submit_search"}, {"action":"wait_for","selector":".features_items"}, {"action":"click","selector":".productinfo.text-center:has-text('Blue Top') a:has-text('View Product')"}, {"action":"wait_for","selector":".product-information"}, {"action":"read_text","selector":".product-information span.price"} ] } </code></pre> <h3>How It Works</h3>

<b>BrowserSession</b>: context manager (Chromium, context/page, timeouts, cleanup)<br>

<b>SiteAdapter</b>: strategy interface; <i>AutomationExerciseAdapter</i> implements login/sign-up/search/price<br>

<b>AuthService / CatalogService</b>: site-agnostic orchestration<br>

<h3>Troubleshooting</h3>

<b>ModuleNotFoundError: RobotDriver</b> → run from repo root: <code>python -m RobotDriver.Main ...</code><br>

<b>Browsers missing</b> → <code>python -m playwright install</code><br>

<b>Timeouts</b> → increase timeouts in <code>Core/Session.py</code> or add <code>wait_for_*</code> in adapter<br>

<h3>Security</h3>

Do <b>not</b> commit real credentials. Use <code>AE_EMAIL</code> / <code>AE_PASSWORD</code> env vars for demos.

<h3>License</h3>

MIT
