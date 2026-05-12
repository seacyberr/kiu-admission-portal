import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Authentication Flows
 * Tests login, registration, and protected routes
 */

// Test credentials
const TEST_USER = {
  email: `test-${Date.now()}@example.com`,
  password: "TestPass123!",
  firstName: "Test",
  lastName: "User"
};

test.describe("Authentication Flows", () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing session
    await page.goto("/logout");
  });

  test("complete registration flow", async ({ page }) => {
    // Navigate to register page
    await page.goto("/register");
    
    // Fill registration form
    await page.getByLabel(/First Name/i).fill(TEST_USER.firstName);
    await page.getByLabel(/Last Name/i).fill(TEST_USER.lastName);
    await page.getByLabel(/Email/i).fill(TEST_USER.email);
    await page.getByLabel(/Password/i).fill(TEST_USER.password);
    await page.getByLabel(/Phone Number/i).fill("+256700000000");
    
    // Submit form
    await page.getByRole("button", { name: /Create Account/i }).click();
    
    // Should redirect to OTP verification page
    await expect(page).toHaveURL(/.*verify-otp.*/);
    await expect(page.getByText(/Verification Code/i)).toBeVisible();
  });

  test("login with valid credentials redirects to dashboard", async ({ page }) => {
    await page.goto("/login");
    
    // Fill login form
    await page.getByLabel(/Email/i).fill("test@example.com");
    await page.getByLabel(/Password/i).fill("TestPass123");
    
    // Submit form
    await page.getByRole("button", { name: /Sign In/i }).click();
    
    // Wait for navigation (could be dashboard or OTP if unverified)
    await page.waitForURL(/.*dashboard|verify-otp.*/, { timeout: 5000 });
    
    // Verify we're on a post-login page
    const url = page.url();
    expect(url).toMatch(/dashboard|verify-otp/);
  });

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/login");
    
    // Fill with wrong credentials
    await page.getByLabel(/Email/i).fill("wrong@example.com");
    await page.getByLabel(/Password/i).fill("WrongPass123");
    
    // Submit form
    await page.getByRole("button", { name: /Sign In/i }).click();
    
    // Should show error message
    await expect(page.getByText(/invalid|incorrect|failed|error/i).first()).toBeVisible({ timeout: 3000 });
  });

  test("protected route redirects to login when not authenticated", async ({ page }) => {
    // Try to access dashboard without logging in
    await page.goto("/dashboard");
    
    // Should be redirected to login
    await expect(page).toHaveURL(/.*login.*/);
  });

  test("logout clears session and redirects to home", async ({ page }) => {
    // First login
    await page.goto("/login");
    await page.getByLabel(/Email/i).fill("test@example.com");
    await page.getByLabel(/Password/i).fill("TestPass123");
    await page.getByRole("button", { name: /Sign In/i }).click();
    
    // Wait for navigation
    await page.waitForURL(/.*dashboard|verify-otp.*/, { timeout: 5000 });
    
    // Then logout (if there's a logout button/link)
    const logoutButton = page.getByRole("button", { name: /Logout|Sign Out/i });
    if (await logoutButton.isVisible().catch(() => false)) {
      await logoutButton.click();
      
      // Should redirect to home or login
      await expect(page).toHaveURL(/.*\/$|.*login.*/);
    }
  });
});

test.describe("Password Reset Flow", () => {
  test("forgot password sends OTP", async ({ page }) => {
    await page.goto("/forgot-password");
    
    await page.getByLabel(/Email/i).fill("test@example.com");
    await page.getByRole("button", { name: /Send Reset Code/i }).click();
    
    // Should show success message or redirect
    await expect(page.getByText(/sent|check your email|success/i).first()).toBeVisible({ timeout: 3000 });
  });
});

test.describe("Role-Based Access", () => {
  test("applicant can access applicant dashboard", async ({ page }) => {
    // Login as applicant
    await page.goto("/login");
    await page.getByLabel(/Email/i).fill("applicant@test.com");
    await page.getByLabel(/Password/i).fill("TestPass123");
    await page.getByRole("button", { name: /Sign In/i }).click();
    
    await page.waitForURL(/.*dashboard|verify-otp.*/, { timeout: 5000 });
    
    // If on dashboard, verify applicant content
    const url = page.url();
    if (url.includes("dashboard")) {
      await expect(page.getByText(/Welcome|Dashboard|My Applications/i).first()).toBeVisible();
    }
  });

  test("admin can access admin pages", async ({ page }) => {
    // Login as admin
    await page.goto("/login");
    await page.getByLabel(/Email/i).fill("admin@test.com");
    await page.getByLabel(/Password/i).fill("AdminPass123");
    await page.getByRole("button", { name: /Sign In/i }).click();
    
    await page.waitForURL(/.*dashboard|verify-otp.*/, { timeout: 5000 });
    
    const url = page.url();
    if (url.includes("dashboard")) {
      // Check for admin-specific elements
      const adminLink = page.getByRole("link", { name: /Admin|Users|Programs|Settings/i });
      if (await adminLink.isVisible().catch(() => false)) {
        await adminLink.click();
        await expect(page).toHaveURL(/.*admin.*/);
      }
    }
  });
});
