import { pgTable, text, serial, varchar, integer, timestamp, date, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { usersTable } from "./users";
import { programsTable } from "./programs";

export const admissionApplicationsTable = pgTable("admission_applications", {
  id: serial("id").primaryKey(),
  applicationNumber: varchar("application_number", { length: 30 }).notNull().unique(),
  userId: integer("user_id").notNull().references(() => usersTable.id),
  programId: integer("program_id").notNull().references(() => programsTable.id),
  status: varchar("status", { length: 30 }).notNull().default("pending"),
  examLevel: varchar("exam_level", { length: 20 }).notNull(),
  examYear: integer("exam_year").notNull(),
  indexNumber: varchar("index_number", { length: 50 }).notNull(),
  unebGrades: jsonb("uneb_grades").notNull().default([]),
  personalStatement: text("personal_statement"),
  dateOfBirth: date("date_of_birth").notNull(),
  gender: varchar("gender", { length: 20 }).notNull(),
  nationality: varchar("nationality", { length: 100 }).default("Ugandan"),
  district: varchar("district", { length: 100 }),
  nextOfKinName: varchar("next_of_kin_name", { length: 200 }),
  nextOfKinPhone: varchar("next_of_kin_phone", { length: 20 }),
  nextOfKinRelationship: varchar("next_of_kin_relationship", { length: 50 }),
  adminNotes: text("admin_notes"),
  submittedAt: timestamp("submitted_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertAdmissionApplicationSchema = createInsertSchema(admissionApplicationsTable).omit({
  id: true, submittedAt: true, updatedAt: true
});
export type InsertAdmissionApplication = z.infer<typeof insertAdmissionApplicationSchema>;
export type AdmissionApplication = typeof admissionApplicationsTable.$inferSelect;
