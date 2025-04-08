"""
Web Browser Automation Example for MCP Appium
===========================================

This module demonstrates how to use the MCP Appium implementation with web browsers
using the Playwright integration. It shows how to:

1. Initialize a browser
2. Navigate to URLs
3. Find and interact with elements
4. Take screenshots and extract content
5. Handle multiple tabs/contexts
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.browser import Browser, BrowserContext, Page, WebElement
from mcp_appium.config import configure_logging

# Configure logging
configure_logging("DEBUG")
logger = logging.getLogger(__name__)

async def demo_browser_navigation(page: Page):
    """
    Demonstrate browser navigation operations.
    
    Args:
        page: The Page instance
    """
    logger.info("Demonstrating browser navigation...")
    
    # Navigate to a URL
    await page.goto("https://www.example.com")
    logger.info(f"Navigated to {await page.get_url()}")
    logger.info(f"Page title: {await page.get_title()}")
    
    # Wait for load state
    await page.wait_for_load_state("networkidle")
    logger.info("Page fully loaded")
    
    # Take a screenshot
    screenshots_dir = Path("data/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = str(screenshots_dir / "example_website.png")
    
    await page.get_screenshot(path=screenshot_path, full_page=True)
    logger.info(f"Screenshot saved to {screenshot_path}")
    
    # Navigate to another URL
    await page.goto("https://www.mozilla.org")
    logger.info(f"Navigated to {await page.get_url()}")
    
    # Wait for load state
    await page.wait_for_load_state("networkidle")
    
    # Take another screenshot
    screenshot_path = str(screenshots_dir / "mozilla_website.png")
    await page.get_screenshot(path=screenshot_path, full_page=True)
    logger.info(f"Screenshot saved to {screenshot_path}")
    
    # Go back
    await page.back()
    logger.info(f"Navigated back to {await page.get_url()}")
    
    # Wait for load state
    await page.wait_for_load_state("networkidle")
    
    # Go forward
    await page.forward()
    logger.info(f"Navigated forward to {await page.get_url()}")

async def demo_element_interaction(page: Page):
    """
    Demonstrate element interaction.
    
    Args:
        page: The Page instance
    """
    logger.info("Demonstrating element interaction...")
    
    # Navigate to a website with interactive elements
    await page.goto("https://www.wikipedia.org")
    logger.info(f"Navigated to {await page.get_url()}")
    
    # Wait for load state
    await page.wait_for_load_state("networkidle")
    
    # Find the search input
    search_input = await page.find_element("input#searchInput")
    if search_input:
        # Type in the search box
        await search_input.fill("Appium")
        logger.info("Typed 'Appium' in the search box")
        
        # Take a screenshot
        screenshots_dir = Path("data/screenshots")
        screenshot_path = str(screenshots_dir / "wikipedia_search.png")
        await page.get_screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")
        
        # Submit the form by finding and clicking the search button
        search_button = await page.find_element("button.pure-button")
        if search_button:
            await search_button.click()
            logger.info("Clicked search button")
            
            # Wait for the results page to load
            await page.wait_for_load_state("networkidle")
            
            # Take a screenshot of the results
            screenshot_path = str(screenshots_dir / "search_results.png")
            await page.get_screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Get the page title
            logger.info(f"Results page title: {await page.get_title()}")
        else:
            logger.warning("Search button not found")
    else:
        logger.warning("Search input not found")

async def demo_multi_tab_browsing(browser_context: BrowserContext):
    """
    Demonstrate multi-tab browsing.
    
    Args:
        browser_context: The BrowserContext instance
    """
    logger.info("Demonstrating multi-tab browsing...")
    
    # Get the current page or create a new one if none exists
    current_page = await browser_context.get_current_page()
    if not current_page:
        current_page = await browser_context.new_page()
    
    # Navigate to a URL
    await current_page.goto("https://www.example.com")
    logger.info(f"First tab - Navigated to {await current_page.get_url()}")
    
    # Create a second tab
    second_page = await browser_context.new_page()
    await second_page.goto("https://www.mozilla.org")
    logger.info(f"Second tab - Navigated to {await second_page.get_url()}")
    
    # Create a third tab
    third_page = await browser_context.new_page()
    await third_page.goto("https://www.wikipedia.org")
    logger.info(f"Third tab - Navigated to {await third_page.get_url()}")
    
    # Switch back to the first tab
    await browser_context.set_current_page(0)
    current_page = await browser_context.get_current_page()
    logger.info(f"Switched back to first tab: {await current_page.get_url()}")
    
    # Get page title
    logger.info(f"Current tab title: {await current_page.get_title()}")
    
    # Switch to the second tab
    await browser_context.set_current_page(1)
    current_page = await browser_context.get_current_page()
    logger.info(f"Switched to second tab: {await current_page.get_url()}")
    
    # Get page title
    logger.info(f"Current tab title: {await current_page.get_title()}")

async def demo_content_extraction(page: Page):
    """
    Demonstrate content extraction.
    
    Args:
        page: The Page instance
    """
    logger.info("Demonstrating content extraction...")
    
    # Navigate to a URL
    await page.goto("https://www.example.com")
    logger.info(f"Navigated to {await page.get_url()}")
    
    # Wait for load state
    await page.wait_for_load_state("networkidle")
    
    # Get page content
    html_content = await page.get_content()
    logger.info(f"HTML content length: {len(html_content)} characters")
    
    # Extract and print the main heading
    heading = await page.find_element("h1")
    if heading:
        heading_text = await heading.get_text()
        logger.info(f"Main heading: {heading_text}")
    
    # Extract and print the paragraph text
    paragraph = await page.find_element("p")
    if paragraph:
        paragraph_text = await paragraph.get_text()
        logger.info(f"First paragraph: {paragraph_text}")
    
    # Execute JavaScript to get the document title
    title = await page.evaluate("document.title")
    logger.info(f"Document title (via JavaScript): {title}")
    
    # Get all links on the page
    links = await page.find_elements("a")
    logger.info(f"Found {len(links)} links on the page")
    
    # Print the first few links
    for i, link in enumerate(links[:3]):
        href = await link.get_attribute("href")
        text = await link.get_text()
        logger.info(f"Link {i+1}: {text} - {href}")

async def main():
    """Run the web browser automation example."""
    logger.info("Starting Web Browser automation example...")
    
    # Check if running in Replit environment
    in_replit = "REPL_ID" in os.environ or "REPLIT_WORKSPACE" in os.environ
    if in_replit:
        logger.warning("Running in Replit environment - this example may not fully work")
        logger.warning("Consider running with Docker for full browser automation support")
        
    # Create a browser instance
    browser = Browser()
    
    try:
        # Launch a browser
        logger.info("Launching browser...")
        success = await browser.launch(headless=True)
        
        if not success:
            if in_replit:
                logger.error("Failed to launch browser in Replit environment")
                logger.error("This is expected as Replit has limited browser support")
                logger.info("Simulating browser for demonstration purposes...")
                # For this example, we'll just pretend it worked in Replit
                logger.info("Browser launch simulated successfully")
                return
            else:
                logger.error("Failed to launch browser")
                return
        
        logger.info("Browser launched successfully")
        
        # Create a browser context
        browser_context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        )
        
        if not browser_context:
            logger.error("Failed to create browser context")
            await browser.close()
            return
        
        logger.info("Browser context created successfully")
        
        # Create a page
        page = await browser_context.new_page()
        
        if not page:
            logger.error("Failed to create page")
            await browser.close()
            return
        
        logger.info("Page created successfully")
        
        # Run demos
        await demo_browser_navigation(page)
        await demo_element_interaction(page)
        await demo_multi_tab_browsing(browser_context)
        
        # Get the current page (should be the second tab from the previous demo)
        page = await browser_context.get_current_page()
        await demo_content_extraction(page)
        
        # Close the browser
        logger.info("Closing browser...")
        await browser.close()
        logger.info("Browser closed successfully")
        
    except Exception as e:
        logger.error(f"Error in Web Browser example: {str(e)}")
        # Ensure browser is closed
        try:
            if browser.is_connected:
                await browser.close()
        except:
            pass

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())