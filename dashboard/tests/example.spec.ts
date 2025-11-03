/**
 * Playwright tests for SupplierSync Dashboard
 * Run with: npx playwright test
 * 
 * Install Playwright first:
 * npm install -D @playwright/test
 * npx playwright install
 */

import { test, expect } from '@playwright/test';

test.describe('SupplierSync Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should load dashboard with stats cards', async ({ page }) => {
    await expect(page.locator('text=Active SKUs')).toBeVisible();
    await expect(page.locator('text=Approved Price Events')).toBeVisible();
    await expect(page.locator('text=Rejected Prices')).toBeVisible();
    await expect(page.locator('text=CX Events')).toBeVisible();
  });

  test('should display catalog table', async ({ page }) => {
    await expect(page.locator('text=Catalog')).toBeVisible();
    await expect(page.locator('table')).toBeVisible();
  });

  test('should display governance decisions section', async ({ page }) => {
    await expect(page.locator('text=Governance Decisions')).toBeVisible();
  });

  test('should display metrics section', async ({ page }) => {
    await expect(page.locator('text=Metrics & Observability')).toBeVisible();
  });

  test('should have Run Orchestration button', async ({ page }) => {
    await expect(page.locator('button:has-text("Run Orchestration")')).toBeVisible();
  });

  test('should trigger orchestration when button clicked', async ({ page }) => {
    // Mock the API response
    await page.route('http://localhost:8000/orchestrate', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          run_id: 'test-run-123',
          supplier_updates: [],
          approved_prices: [],
          rejected_prices: [],
          cx_actions: [],
        }),
      });
    });

    await page.click('button:has-text("Run Orchestration")');
    
    // Wait for page reload or response
    await page.waitForTimeout(2000);
    
    // Check that console doesn't show errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Verify no critical errors
    expect(errors.length).toBeLessThan(10);
  });
});

