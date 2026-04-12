# Archive Folder

This folder contains archived code that was removed from the main codebase during industry-standard cleanup.

## Contents

### src-refactoring-YYYYMMDD/
**What**: Attempt at domain-driven architecture refactoring  
**Why archived**: Abandoned in favor of existing working architecture  
**Contains**:
- Domain-driven design pattern with separate api/core/domain/infrastructure layers
- Flask-JWT-Extended based authentication (vs custom JWT in main app)
- Different model schemas and service structure
- NOT integrated with main app.py

**Decision**: Archive rather than delete to preserve significant development effort.

## Cleanup Date
April 12, 2026

## Industry Standards Applied
- DRY (Don't Repeat Yourself) - removed exact duplicates
- YAGNI (You Aren't Gonna Need It) - removed dead code
- Single Source of Truth - consolidated to one auth system
- Preserve History - archived significant work before deletion
