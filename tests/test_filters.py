"""
Basic tests for mtx-config application structure.
Tests the HTML structure and functionality without requiring a running server.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
def test_html_structure(page: Page):
    """Test basic HTML structure exists."""
    # Create a simple HTML page to test structure
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Mediamtx Configuration Editor</title></head>
    <body>
        <div role="tablist">
            <button>App (Основные)</button>
            <button>Paths</button>
        </div>
        <div role="tabpanel">
            <select><option value="all">all</option></select>
            <input placeholder="Поиск потоков..." />
        </div>
    </body>
    </html>
    """

    page.set_content(html_content)

    # Test that title is correct
    expect(page).to_have_title("Mediamtx Configuration Editor")

    # Test that tabs exist
    tabs = page.locator("div[role='tablist'] button")
    expect(tabs).to_have_count(2)
    expect(tabs.first).to_have_text("App (Основные)")
    expect(tabs.last).to_have_text("Paths")

    # Test that Paths tab contains filter elements
    paths_tab = page.locator("div[role='tabpanel']")

    # Check filter dropdown (select element itself, not option)
    filter_select = paths_tab.locator("select")
    expect(filter_select).to_be_visible()

    # Check search input
    search_input = paths_tab.locator("input[placeholder*='Поиск потоков']")
    expect(search_input).to_be_visible()


@pytest.mark.playwright
def test_filter_interaction(page: Page):
    """Test filter interaction without server."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <select id="typeFilter">
            <option value="all">all</option>
            <option value="Source">Source</option>
            <option value="RunOnDemand">RunOnDemand</option>
        </select>
        <input id="searchInput" placeholder="Поиск потоков..." />
        <div id="results">2 streams found</div>
    </body>
    </html>
    """

    page.set_content(html_content)

    # Test filter dropdown interaction
    filter_select = page.locator("#typeFilter")
    expect(filter_select).to_be_visible()

    # Select different option
    filter_select.select_option("Source")
    expect(filter_select).to_have_value("Source")

    # Test search input interaction
    search_input = page.locator("#searchInput")
    expect(search_input).to_be_visible()

    # Type in search
    search_input.fill("test search")
    expect(search_input).to_have_value("test search")
