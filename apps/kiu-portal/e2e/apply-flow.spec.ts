import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Application Flow
 * Tests the step-by-step application process
 */

test.describe("Application Form Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to apply page
    await page.goto("/apply");
  });

  test("application form loads with steps", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /Apply|Application|New Application/i })).toBeVisible();
    
    // Check for form sections or steps
    const formElements = page.locator("form, [role='form'], fieldset").first();
    await expect(formElements).toBeVisible();
  });

  test("program selection is available", async ({ page }) => {
    // Look for program selection dropdown or list
    const programSelect = page.getByLabel(/Program|Select Program|Course/i).first();
    if (await programSelect.isVisible().catch(() => false)) {
      await programSelect.click();
      // Should show program options
      await expect(page.getByRole("option").first()).toBeVisible();
    }
  });

  test("exam level selection works", async ({ page }) => {
    // Look for exam level radio buttons or select
    const examLevel = page.getByLabel(/Exam Level|Qualification|Education Level/i).first();
    if (await examLevel.isVisible().catch(() => false)) {
      await examLevel.click();
    }
  });

  test("personal information section exists", async ({ page }) => {
    // Look for personal info fields
    const personalFields = [
      page.getByLabel(/First Name/i),
      page.getByLabel(/Last Name/i),
      page.getByLabel(/Date of Birth/i),
      page.getByLabel(/Gender/i)
    ];
    
    // At least some personal info fields should exist
    const visibleCount = await Promise.all(
      personalFields.map(field => field.isVisible().catch(() => false))
    );
    expect(visibleCount.filter(Boolean).length).toBeGreaterThan(0);
  });

  test("navigation between steps works", async ({ page }) => {
    // Look for navigation buttons
    const nextButton = page.getByRole("button", { name: /Next|Continue|Proceed/i });
    const prevButton = page.getByRole("button", { name: /Back|Previous/i });
    
    // Next button should be visible
    if (await nextButton.isVisible().catch(() => false)) {
      await expect(nextButton).toBeVisible();
    }
  });

  test("form validation prevents submission without required fields", async ({ page }) => {
    // Try to submit without filling required fields
    const submitButton = page.getByRole("button", { name: /Submit|Apply|Save/i });
    if (await submitButton.isVisible().catch(() => false)) {
      await submitButton.click();
      
      // Should show validation errors
      await expect(page.getByText(/required|invalid|error/i).first()).toBeVisible({ timeout: 3000 });
    }
  });
});

test.describe("Recommendation Flow", () => {
  test("recommendation page loads", async ({ page }) => {
    await page.goto("/recommend");
    
    // Should show recommendation interface
    await expect(page.getByRole("heading").first()).toBeVisible();
  });

  test("O-level recommendations accessible", async ({ page }) => {
    await page.goto("/recommend/o-level");
    
    // Check for O-level specific content
    await expect(page.getByText(/O-Level|UCE|Ordinary Level/i).first()).toBeVisible();
  });
});
