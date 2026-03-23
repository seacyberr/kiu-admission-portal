import { pgTable, text, serial, varchar, integer, real, jsonb, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { usersTable } from "./users";
import { programsTable } from "./programs";

export const finalistProfilesTable = pgTable("finalist_profiles", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => usersTable.id).unique(),
  programId: integer("program_id").notNull().references(() => programsTable.id),
  studentNumber: varchar("student_number", { length: 50 }).notNull(),
  yearOfStudy: integer("year_of_study").notNull(),
  graduationYear: integer("graduation_year"),
  gpa: real("gpa"),
  skills: jsonb("skills").default([]),
  bio: text("bio"),
  linkedinUrl: text("linkedin_url"),
  cvUrl: text("cv_url"),
  isFinalist: boolean("is_finalist").default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertFinalistProfileSchema = createInsertSchema(finalistProfilesTable).omit({
  id: true, createdAt: true, updatedAt: true
});
export type InsertFinalistProfile = z.infer<typeof insertFinalistProfileSchema>;
export type FinalistProfile = typeof finalistProfilesTable.$inferSelect;
