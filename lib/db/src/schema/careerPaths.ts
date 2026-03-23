import { pgTable, text, serial, varchar, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const careerPathsTable = pgTable("career_paths", {
  id: serial("id").primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  description: text("description").notNull(),
  relatedPrograms: jsonb("related_programs").notNull().default([]),
  skills: jsonb("skills").notNull().default([]),
  potentialRoles: jsonb("potential_roles").notNull().default([]),
  averageSalaryRange: varchar("average_salary_range", { length: 100 }),
  growthOutlook: varchar("growth_outlook", { length: 100 }),
  industryField: varchar("industry_field", { length: 100 }).notNull(),
});

export const insertCareerPathSchema = createInsertSchema(careerPathsTable).omit({ id: true });
export type InsertCareerPath = z.infer<typeof insertCareerPathSchema>;
export type CareerPath = typeof careerPathsTable.$inferSelect;
