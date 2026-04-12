# Testing Guide - KIU Admission Portal

## Test Organization with Priority Markers

### Priority Levels

| Marker | Description | Test Count | When to Run |
|--------|-------------|------------|-------------|
| `@pytest.mark.critical` | Core functionality - system breaks without these | ~60 | **Always** - Every commit |
| `@pytest.mark.important` | Major features - should work for production | ~80 | **CI/CD** - Before merge |
| `@pytest.mark.extended` | Edge cases, extras - nice to have | ~45 | **Nightly** - Full regression |

### Category Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.auth` | Authentication & authorization tests |
| `@pytest.mark.admission` | Admission pathway tests |
| `@pytest.mark.admin` | Admin operation tests |
| `@pytest.mark.career` | Career portal tests |
| `@pytest.mark.pathway` | Education pathway tests |

---

## Running Tests by Priority

### Critical Tests Only (Quick - ~60 tests)
```bash
# During development - fast feedback
pytest -m critical -v

# Expected: ~2 minutes
```

### Important + Critical (Standard - ~100 tests)
```bash
# CI/CD pipeline
pytest -m "critical or important" -v

# Expected: ~5 minutes
```

### All Tests (Full Suite - 185+ tests)
```bash
# Before release - full regression
pytest -v

# Or with markers
pytest -m "critical or important or extended" -v

# Expected: ~10 minutes
```

---

## Running Tests by Category

```bash
# Authentication only
pytest -m auth -v

# Admission pathways only
pytest -m admission -v

# Admin operations only
pytest -m admin -v

# Career portal only
pytest -m career -v

# Combined categories
pytest -m "auth or admission" -v
```

---

## Development Workflow

### 1. Local Development (Quick Check)
```bash
# Make changes to code
# Run only critical tests for fast feedback
pytest -m critical --tb=short -q
```

### 2. Feature Complete (Standard Check)
```bash
# Run important + critical before committing
pytest -m "critical or important" --tb=short
```

### 3. Pre-Release (Full Check)
```bash
# Run all tests with coverage
pytest -v --cov=src --cov-report=html
```

---

## CI/CD Pipeline Integration

### GitHub Actions Example
```yaml
jobs:
  quick-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest -m critical -v --tb=short

  standard-test:
    runs-on: ubuntu-latest
    needs: quick-test
    steps:
      - uses: actions/checkout@v4
      - run: pytest -m "critical or important" -v

  full-test:
    runs-on: ubuntu-latest
    needs: standard-test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: pytest -v --cov=src
```

---

## Test Statistics

| Suite | Tests | Coverage | Run Time |
|-------|-------|----------|----------|
| Critical | ~60 | 32% | ~2 min |
| Important | ~80 | 43% | ~3 min |
| Extended | ~45 | 24% | ~5 min |
| **Total** | **185+** | **100%** | **~10 min** |

---

## Adding Markers to New Tests

```python
import pytest

class TestMyFeature:
    @pytest.mark.critical
    def test_core_functionality(self, client):
        """This MUST work - core feature"""
        assert True
    
    @pytest.mark.important
    def test_major_feature(self, client):
        """This SHOULD work - major feature"""
        assert True
    
    @pytest.mark.extended
    def test_edge_case(self, client):
        """Nice to have - edge case"""
        assert True
```

---

## Configuration

All markers are defined in `pytest.ini`:

```ini
markers =
    critical: Critical tests - must always pass
    important: Important tests - should run in CI
    extended: Extended tests - nice to have
    auth: Authentication tests
    admission: Admission pathway tests
    admin: Admin operation tests
    career: Career portal tests
    pathway: Education pathway tests
```

---

## Quick Reference Card

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `pytest -m critical` | Run only critical tests | During development |
| `pytest -m important` | Run important tests | Pre-commit |
| `pytest -m extended` | Run extended tests | Nightly builds |
| `pytest -m "critical or important"` | Run standard suite | CI/CD |
| `pytest -m auth` | Run auth tests | Auth changes |
| `pytest -m admission` | Run admission tests | Admission changes |
| `pytest -k test_name` | Run specific test | Debugging |
| `pytest --tb=short` | Short traceback | Quick feedback |
| `pytest --tb=long` | Full traceback | Debugging |
| `pytest -x` | Stop on first fail | Fast fail |
| `pytest -v` | Verbose output | Full visibility |
| `pytest -q` | Quiet mode | Minimal output |

---

## Troubleshooting

### Tests Not Found?
```bash
# Ensure pytest.ini is in root
ls pytest.ini

# Check test file naming
ls tests/test_*.py
```

### Markers Not Recognized?
```bash
# List all markers
pytest --markers

# Should show: critical, important, extended, auth, etc.
```

### Want to Skip Slow Tests?
```bash
# Skip extended tests
pytest -m "not extended" -v
```

---

**Remember**: 
- Critical = System breaks without it
- Important = Users expect it to work  
- Extended = Nice bonus feature
