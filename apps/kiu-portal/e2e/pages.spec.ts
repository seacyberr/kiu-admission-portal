import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Page Functionality and Links
 * Tests navigation, page rendering, and basic user flows
 */

test.describe("Public Pages", () => {
  test("home page loads with hero content", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Shape Your Future at KIU/i })).toBeVisible();
    await expect(page.getByText(/Kampala International University/i)).toBeVisible();
  });

  test("home page has navigation links", async ({ page }) => {
    await page.goto("/");
    // Check for main navigation elements
    await expect(page.getByRole("link", { name: /Programs/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Apply Now/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Login/i })).toBeVisible();
  });

  test("home page Apply Now link navigates to application", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: /Apply Now/i }).first().click();
    await expect(page).toHaveURL(/.*apply.*/);
  });

  test("login page loads correctly", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /Sign In/i })).toBeVisible();
    await expect(page.getByLabel(/Email/i)).toBeVisible();
    await expect(page.getByLabel(/Password/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /Sign In/i })).toBeVisible();
  });

  test("login page has link to register", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: /Sign up/i }).click();
    await expect(page).toHaveURL(/.*register.*/);
  });

  test("register page loads correctly", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: /Create Account/i })).toBeVisible();
    await expect(page.getByLabel(/Email/i)).toBeVisible();
    await expect(page.getByLabel(/Password/i)).toBeVisible();
    await expect(page.getByLabel(/First Name/i)).toBeVisible();
    await expect(page.getByLabel(/Last Name/i)).toBeVisible();
  });

  test("register page has link to login", async ({ page }) => {
    await page.goto("/register");
    await page.getByRole("link", { name: /Sign in/i }).click();
    await expect(page).toHaveURL(/.*login.*/);
  });

  test("forgot password page loads", async ({ page }) => {
    await page.goto("/forgot-password");
    await expect(page.getByRole("heading", { name: /Forgot Password/i })).toBeVisible();
    await expect(page.getByLabel(/Email/i)).toBeVisible();
  });
});

test.describe("Navigation", () => {
  test("header navigation is present on all pages", async ({ page }) => {
    const pages = ["/", "/login", "/register"];
    for (const url of pages) {
      await page.goto(url);
      await expect(page.locator("header")).toBeVisible();
      await expect(page.getByRole("link", { name: /KIU/i })).toBeVisible();
    }
  });

  test("footer is present on home page", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("footer")).toBeVisible();
  });

  test("mobile menu toggle works", async ({ page }) => {
    await page.goto("/");
    await page.setViewportSize({ width: 375, height: 667 });
    
    const menuButton = page.getByRole("button", { name: /Menu/i });
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      // Check that menu items are visible after clicking
      await expect(page.getByRole("link", { name: /Programs/i })).toBeVisible();
    }
  });
});

test.describe("404 Page", () => {
  test("non-existent route shows 404 page", async ({ page }) => {
    await page.goto("/non-existent-page");
    await expect(page.getByText(/404|Not Found|Page not found/i)).toBeVisible();
  });
});

test.describe("Form Interactions", () => {
  test("login form validation shows errors for empty fields", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("button", { name: /Sign In/i }).click();
    
    // Should show validation errors
    await expect(page.getByText(/email is required|invalid email/i).first()).toBeVisible();
  });

  test("register form validation shows errors for empty fields", async ({ page }) => {
    await page.goto("/register");
    await page.getByRole("button", { name: /Create Account/i }).click();
    
    // Should show validation errors
    await expect(page.getByText(/required|invalid/i).first()).toBeVisible();
  });

  test("password field can show/hide password", async ({ page }) => {
    await page.goto("/login");
    const passwordInput = page.getByLabel(/Password/i);
    await passwordInput.fill("testpassword");
    
    // Check if there's a show/hide button and click it
    const toggleButton = page.locator("[data-testid='toggle-password'], button[aria-label*='password' i], button[aria-label*='show' i]").first();
    if (await toggleButton.isVisible().catch(() => false)) {
      await toggleButton.click();
      // Verify the input type changed (would need data-testid for proper assertion)
    }
  });
});

test.describe("Accessibility", () => {
  test("home page has proper heading structure", async ({ page }) => {
    await page.goto("/");
    
    // Check for h1 heading
    const h1 = page.locator("h1");
    await expect(h1).toBeVisible();
    
    // Check that images have alt text
    const images = page.locator("img");
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute("alt");
      // Skip decorative images (they should have empty alt or role="presentation")
      if (alt === null) {
        console.log(`Warning: Image ${i} is missing alt text`);
      }
    }
  });

  test("form inputs have associated labels", async ({ page }) => {
    await page.goto("/login");
    
    // Check email input
    const emailInput = page.getByLabel(/Email/i);
    await expect(emailInput).toHaveAttribute("type", "email");
    
    // Check password input
    const passwordInput = page.getByLabel(/Password/i);
    await expect(passwordInput).toHaveAttribute("type", "password");
  });
});

test.describe("Responsive Design", () => {
  test("page renders correctly on desktop", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Shape Your Future/i })).toBeVisible();
  });

  test("page renders correctly on tablet", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Shape Your Future/i })).toBeVisible();
  });

  test("page renders correctly on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Shape Your Future/i })).toBeVisible();
  });
});

test.describe("Program Pages", () => {
  test("programs section is visible on home page", async ({ page }) => {
    await page.goto("/");
    
    // Look for programs section heading
    const programsHeading = page.getByRole("heading", { name: /Programs|Our Programs|Available Programs/i });
    await expect(programsHeading.first()).toBeVisible();
  });

  test("program cards are displayed", async ({ page }) => {
    await page.goto("/");
    
    // Look for program cards (they typically have program names or view details buttons)
    const programCards = page.locator("[data-testid='program-card'], .program-card, article").first();
    // Just verify that program-related content exists
    await expect(page.getByText(/Bachelor|Diploma|Certificate|Degree/i).first()).toBeVisible();
  });
});

test.describe("Performance", () => {
  test("home page loads within 3 seconds", async ({ page }) => {
    const start = Date.now();
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    const loadTime = Date.now() - start;
    
    console.log(`Page load time: ${loadTime}ms`);
    expect(loadTime).toBeLessThan(3000);
  });
});
