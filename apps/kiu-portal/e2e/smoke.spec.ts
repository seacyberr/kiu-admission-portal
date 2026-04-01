import { test, expect } from "@playwright/test";

test("home page loads hero content", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Shape Your Future at KIU/i })).toBeVisible();
});
