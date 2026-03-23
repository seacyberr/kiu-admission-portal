import { pgTable, text, serial, varchar, integer, timestamp, date, jsonb, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const opportunitiesTable = pgTable("opportunities", {
  id: serial("id").primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  organization: varchar("organization", { length: 255 }).notNull(),
  type: varchar("type", { length: 20 }).notNull(),
  description: text("description").notNull(),
  requirements: text("requirements").notNull(),
  requiredPrograms: jsonb("required_programs").default([]),
  requiredSkills: jsonb("required_skills").default([]),
  location: varchar("location", { length: 255 }),
  salaryRange: varchar("salary_range", { length: 100 }),
  applicationDeadline: date("application_deadline").notNull(),
  contactEmail: varchar("contact_email", { length: 255 }),
  isActive: boolean("is_active").default(true).notNull(),
  postedAt: timestamp("posted_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertOpportunitySchema = createInsertSchema(opportunitiesTable).omit({
  id: true, postedAt: true, updatedAt: true
});
export type InsertOpportunity = z.infer<typeof insertOpportunitySchema>;
export type Opportunity = typeof opportunitiesTable.$inferSelect;
