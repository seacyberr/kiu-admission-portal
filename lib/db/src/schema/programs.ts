import { pgTable, text, serial, varchar, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const programsTable = pgTable("programs", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  code: varchar("code", { length: 20 }).notNull().unique(),
  faculty: varchar("faculty", { length: 255 }).notNull(),
  department: varchar("department", { length: 255 }),
  level: varchar("level", { length: 20 }).notNull(),
  duration: varchar("duration", { length: 50 }),
  description: text("description"),
  entryRequirements: text("entry_requirements"),
  minOlevelPoints: integer("min_olevel_points"),
  minAlevelPoints: integer("min_alevel_points"),
  availableSlots: integer("available_slots").default(100),
});

export const insertProgramSchema = createInsertSchema(programsTable).omit({ id: true });
export type InsertProgram = z.infer<typeof insertProgramSchema>;
export type Program = typeof programsTable.$inferSelect;
