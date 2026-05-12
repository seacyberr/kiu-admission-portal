import { describe, expect, it } from "vitest";
import { isPublicPath } from "./is-public-path";

describe("isPublicPath", () => {
  it("marks marketing and auth routes as public", () => {
    expect(isPublicPath("/")).toBe(true);
    expect(isPublicPath("/login")).toBe(true);
    expect(isPublicPath("/register")).toBe(true);
    expect(isPublicPath("/verify-otp")).toBe(true);
    expect(isPublicPath("/forgot-password")).toBe(true);
  });

  it("marks role dashboards as protected", () => {
    expect(isPublicPath("/dashboard")).toBe(false);
    expect(isPublicPath("/admin")).toBe(false);
    expect(isPublicPath("/career")).toBe(false);
  });
});
