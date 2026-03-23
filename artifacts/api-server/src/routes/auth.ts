import { Router, type IRouter, type Request, type Response } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { db, usersTable } from "@workspace/db";
import { eq } from "drizzle-orm";

const router: IRouter = Router();

const JWT_SECRET = process.env.JWT_SECRET || "kiu-portal-secret-key-2024";

export function generateToken(userId: number, role: string) {
  return jwt.sign({ userId, role }, JWT_SECRET, { expiresIn: "7d" });
}

export function verifyToken(token: string) {
  return jwt.verify(token, JWT_SECRET) as { userId: number; role: string };
}

router.post("/register", async (req: Request, res: Response) => {
  try {
    const { email, password, firstName, lastName, phone, nationalId, role } = req.body;

    if (!email || !password || !firstName || !lastName) {
      res.status(400).json({ error: "Missing required fields", message: "email, password, firstName, lastName are required" });
      return;
    }

    const existing = await db.select().from(usersTable).where(eq(usersTable.email, email)).limit(1);
    if (existing.length > 0) {
      res.status(409).json({ error: "Conflict", message: "An account with this email already exists" });
      return;
    }

    const passwordHash = await bcrypt.hash(password, 10);
    const userRole = role && ["applicant", "finalist", "admin"].includes(role) ? role : "applicant";

    const [user] = await db.insert(usersTable).values({
      email,
      passwordHash,
      firstName,
      lastName,
      phone: phone || null,
      nationalId: nationalId || null,
      role: userRole,
    }).returning();

    const token = generateToken(user.id, user.role);

    res.status(201).json({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        phone: user.phone,
        role: user.role,
        nationalId: user.nationalId,
        createdAt: user.createdAt,
      },
      token,
    });
  } catch (err) {
    req.log.error({ err }, "Register error");
    res.status(500).json({ error: "Internal server error", message: "Registration failed" });
  }
});

router.post("/login", async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: "Missing required fields", message: "email and password are required" });
      return;
    }

    const [user] = await db.select().from(usersTable).where(eq(usersTable.email, email)).limit(1);
    if (!user) {
      res.status(401).json({ error: "Unauthorized", message: "Invalid email or password" });
      return;
    }

    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) {
      res.status(401).json({ error: "Unauthorized", message: "Invalid email or password" });
      return;
    }

    const token = generateToken(user.id, user.role);

    res.json({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        phone: user.phone,
        role: user.role,
        nationalId: user.nationalId,
        createdAt: user.createdAt,
      },
      token,
    });
  } catch (err) {
    req.log.error({ err }, "Login error");
    res.status(500).json({ error: "Internal server error", message: "Login failed" });
  }
});

router.post("/logout", (_req: Request, res: Response) => {
  res.json({ message: "Logged out successfully" });
});

router.get("/me", async (req: Request, res: Response) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      res.status(401).json({ error: "Unauthorized", message: "No token provided" });
      return;
    }
    const token = authHeader.slice(7);
    const decoded = verifyToken(token);

    const [user] = await db.select().from(usersTable).where(eq(usersTable.id, decoded.userId)).limit(1);
    if (!user) {
      res.status(401).json({ error: "Unauthorized", message: "User not found" });
      return;
    }

    res.json({
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      phone: user.phone,
      role: user.role,
      nationalId: user.nationalId,
      createdAt: user.createdAt,
    });
  } catch {
    res.status(401).json({ error: "Unauthorized", message: "Invalid or expired token" });
  }
});

export default router;
