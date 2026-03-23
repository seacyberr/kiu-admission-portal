import { pgTable, text, serial, varchar, integer, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { usersTable } from "./users";
import { opportunitiesTable } from "./opportunities";

export const opportunityApplicationsTable = pgTable("opportunity_applications", {
  id: serial("id").primaryKey(),
  opportunityId: integer("opportunity_id").notNull().references(() => opportunitiesTable.id),
  userId: integer("user_id").notNull().references(() => usersTable.id),
  status: varchar("status", { length: 30 }).notNull().default("applied"),
  coverLetter: text("cover_letter").notNull(),
  cvUrl: text("cv_url"),
  additionalInfo: text("additional_info"),
  adminNotes: text("admin_notes"),
  appliedAt: timestamp("applied_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertOpportunityApplicationSchema = createInsertSchema(opportunityApplicationsTable).omit({
  id: true, appliedAt: true, updatedAt: true
});
export type InsertOpportunityApplication = z.infer<typeof insertOpportunityApplicationSchema>;
export type OpportunityApplication = typeof opportunityApplicationsTable.$inferSelect;
