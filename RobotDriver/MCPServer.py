import re
from typing import Literal, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel

from RobotDriver.Core.Session import BrowserSession

app = FastAPI(title="RobotDriver MCP Server", version="1.0.0")

"""
Playwright MCP server
"""

"""
The model
"""
class Step(BaseModel):
    action: Literal["goto","click","fill","wait_for","wait_url"]
    selector: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None

"""
Plan executed by the server
"""
class Plan(BaseModel):
    steps: List[Step]
    headless: bool = True

"""
Trim an accessibility snapshot to (role/name/value) up to a bounded depth.
"""
def _prune_a11y(node, depth=2, max_children=30):
    if not node: return None
    slim = {k: node.get(k) for k in ("role","name","value")}
    kids = node.get("children") or []
    if depth > 0 and kids:
        slim["children"] = [_prune_a11y(c, depth-1, max_children) for c in kids[:max_children]]
    return slim

"""
Click by CSS selector or (role+name). Returns a short note for logs.
"""
def _click(page, step: Step):
    if step.selector:
        page.locator(step.selector).first.click()
        return "clicked via selector"
    if step.role and step.name:
        page.get_by_role(step.role, name=re.compile(step.name, re.I)).first.click()
        return "clicked via role+name"
    raise ValueError("click requires selector or (role+name)")

"""
Fill by CSS selector or (role+name). Returns a short note for logs.
"""
def _fill(page, step: Step):
    if not step.text:
        raise ValueError("fill requires text")
    if step.selector:
        page.fill(step.selector, step.text)
        return "filled via selector"
    if step.role and step.name:
        page.get_by_role(step.role, name=re.compile(step.name, re.I)).fill(step.text)
        return "filled via role+name"
    raise ValueError("fill requires selector or (role+name)")

"""
Return a trimmed accessibility tree for the given URL.
"""
@app.get("/mcp/describe_page")
def describe_page(url: str = Query(...), depth: int = 2):
    with BrowserSession(headless=True) as s:
        s.page.goto(url, wait_until="domcontentloaded")
        snap = s.page.accessibility.snapshot()
        return {"url": s.page.url, "a11y": _prune_a11y(snap, depth=depth)}

"""
Execute a plan step-by-step and return action logs.
"""
@app.post("/mcp/execute_plan")
def execute_plan(plan: Plan):
    logs = []
    with BrowserSession(headless=plan.headless) as s:
        for i, step in enumerate(plan.steps, start=1):
            try:
                if step.action == "goto":
                    if not step.url: raise ValueError("goto requires url")
                    s.page.goto(step.url, wait_until="domcontentloaded")
                    logs.append({"i": i, "action": "goto", "url": s.page.url, "ok": True})
                elif step.action == "click":
                    note = _click(s.page, step)
                    logs.append({"i": i, "action": "click", "note": note, "ok": True})
                elif step.action == "fill":
                    note = _fill(s.page, step)
                    logs.append({"i": i, "action": "fill", "note": note, "ok": True})
                elif step.action == "wait_for":
                    if not step.selector: raise ValueError("wait_for requires selector")
                    s.page.wait_for_selector(step.selector, state="visible")
                    logs.append({"i": i, "action": "wait_for", "selector": step.selector, "ok": True})
                elif step.action == "wait_url":
                    if not step.url: raise ValueError("wait_url requires url")
                    s.page.wait_for_url(step.url)
                    logs.append({"i": i, "action": "wait_url", "url": step.url, "ok": True})
                elif step.action == "read_text":
                    if not step.selector:
                        raise ValueError("read_text requires selector")
                    txt = s.page.locator(step.selector).first.inner_text().strip()
                    logs.append({"i": i, "action": "read_text", "selector": step.selector, "text": txt, "ok": True})
                elif step.action == "screenshot":
                    path = step.text or f"snap_{i}.png"
                    s.page.screenshot(path=path, full_page=True)
                    logs.append({"i": i, "action": "screenshot", "path": path, "ok": True})
                else:
                    logs.append({"i": i, "action": step.action, "ok": False, "error": "unknown_action"})
            except Exception as e:
                logs.append({"i": i, "action": step.action, "ok": False, "error": str(e)})
                break
        return {"ok": logs and logs[-1].get("ok", False), "current_url": s.page.url, "logs": logs}