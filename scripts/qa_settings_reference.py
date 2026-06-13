from playwright.sync_api import sync_playwright
from pathlib import Path

DESIGN = (
    Path(__file__).parents[1]
    / "docs/design/spreadsheets/project/Excel Update Tool · standalone.html"
).resolve()
OUT = Path(__file__).parents[1] / "docs/qa/reference"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    page.goto(f"file://{DESIGN}")
    page.wait_for_timeout(1500)  # let React + Babel render

    # V1 artboard is the second dc-card (1280x820).  Use nth(1) to target it.
    v1_card = page.locator(".dc-card").nth(1)

    # Navigate the V1 interactive app to Configure view.
    v1_card.locator(".v1-side-item", has_text="Configure").click()
    page.wait_for_timeout(400)

    # Screenshot the entire V1 artboard.
    v1_card.screenshot(path=str(OUT / "settings_populated.png"))

    # Also clip just the two-pane area (below the global card, below title bar).
    # Title bar ~32px, global card ~80px => pane area starts at ~112px.
    page.screenshot(
        path=str(OUT / "settings_panes.png"),
        clip={
            "x": v1_card.bounding_box()["x"],
            "y": v1_card.bounding_box()["y"] + 112,
            "width": 1280,
            "height": 708,
        },
    )

    browser.close()

print("Saved to docs/qa/reference/")
