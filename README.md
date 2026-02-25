# 🎭 SauceDemo Playwright Test Automation Framework

A **production-grade**, **scalable**, and **maintainable** End-to-End (E2E) testing framework built with **Playwright** for Python and **pytest**. This framework demonstrates modern software architecture principles, clean code practices, and comprehensive test automation patterns.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-1.41+-green.svg)](https://playwright.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-8.0+-orange.svg)](https://docs.pytest.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running Tests](#-running-tests)
- [Test Organization](#-test-organization)
- [Reporting](#-reporting)
- [CI/CD Integration](#-cicd-integration)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This framework automates end-to-end testing for the **SauceDemo** e-commerce application (https://www.saucedemo.com/). It's designed as a **learning resource** and **portfolio project** that showcases:

- **Clean Architecture** with clear separation of concerns
- **Page Object Model (POM)** pattern for maintainability
- **Async/await** patterns with Playwright
- **Comprehensive logging** and error handling
- **Parallel test execution** for faster feedback
- **CI/CD integration** with GitLab and GitHub Actions

### 🎓 Learning Objectives

This framework is designed to help you:
- Understand modern test automation architecture
- Learn Playwright and pytest best practices
- Master async Python programming patterns
- Implement Page Object Model effectively
- Set up CI/CD pipelines for test automation

---

## ✨ Key Features

### Framework Capabilities

- ✅ **Multi-Browser Support**: Chromium, Firefox, WebKit
- ✅ **Parallel Execution**: Run tests concurrently for faster results
- ✅ **Cross-Platform**: Works on Linux, macOS, Windows
- ✅ **Environment Management**: Separate configs for dev/staging/prod
- ✅ **Authentication Persistence**: Login once, reuse across tests
- ✅ **Comprehensive Reporting**: HTML, Allure, and custom reports
- ✅ **Auto Screenshots**: Capture screenshots on test failures
- ✅ **Video Recording**: Record test execution videos
- ✅ **Tracing**: Full Playwright trace for debugging
- ✅ **Retry Logic**: Automatic test retries on failure

### Code Quality Features

- ✅ **Type Hints**: Full type annotation for better IDE support
- ✅ **Linting**: Ruff for fast Python linting
- ✅ **Formatting**: Black for consistent code style
- ✅ **Type Checking**: MyPy for static type verification
- ✅ **Docstrings**: Comprehensive documentation for all modules

---

## 🏗️ Architecture

For a senior-level architecture review and roadmap (including AI extensibility), see `docs/ARCHITECTURE_REVIEW.md`.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Test Framework                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────┐      ┌─────────────┐      ┌────────────┐       │
│  │   Tests    │─────▶│   Pages     │─────▶│  Base Page │       │
│  │  (Specs)   │      │   (POM)     │      │            │       │
│  └────────────┘      └─────────────┘      └────────────┘       │
│        │                    │                     │              │
│        ▼                    ▼                     ▼              │
│  ┌────────────┐      ┌─────────────┐      ┌────────────┐       │
│  │  Fixtures  │◀─────│   Config    │◀─────│   Utils    │       │
│  │  (pytest)  │      │  (Settings) │      │ (Helpers)  │       │
│  └────────────┘      └─────────────┘      └────────────┘       │
│                              │                                    │
│                              ▼                                    │
│                      ┌──────────────┐                            │
│                      │  Playwright  │                            │
│                      │    Engine    │                            │
│                      └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
saucedemo-playwright-framework/
│
├── config/                      # Configuration management
│   ├── __init__.py
│   └── settings.py             # Pydantic settings with validation
│
├── pages/                       # Page Object Model (POM)
│   ├── __init__.py
│   ├── base_page.py           # Base page with common methods
│   ├── login_page.py          # Login page object
│   ├── products_page.py       # Products/inventory page
│   ├── cart_page.py           # Shopping cart page
│   ├── checkout/              # Checkout pages split by step
│   │   ├── info_page.py
│   │   ├── overview_page.py
│   │   └── complete_page.py
│   └── checkout_page.py       # Backward-compatible re-export
│
├── tests/                       # Test specifications
│   ├── login/                 # Login tests
│   ├── products/              # Product browsing tests
│   ├── cart/                  # Cart management tests
│   ├── checkout/              # Checkout flow tests
│   └── e2e/                   # End-to-end tests
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── logger.py              # Centralized logging
│   ├── helpers.py             # Helper functions
│   ├── exceptions.py          # Custom exceptions
│   └── decorators.py          # Function decorators
│
├── reports/                     # Generated test reports
├── logs/                        # Test execution logs
├── .github/workflows/          # GitHub Actions workflows
│
├── conftest.py                 # Global pytest configuration
├── pytest.ini                  # Pytest settings
├── pyproject.toml             # Project metadata and tool configs
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitlab-ci.yml             # GitLab CI/CD configuration
└── README.md                  # This file
```

---

## 🔧 Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (Python package manager)
- **Git** ([Download](https://git-scm.com/downloads))

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd playwrightExample
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Install browser dependencies (Linux only)
playwright install-deps
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### 5. Verify Installation

```bash
# Run a quick test to verify setup
pytest tests/login/test_login.py::TestLoginSuccess::test_login_with_standard_user -v
```

---

## ⚙️ Configuration

The framework uses environment variables for configuration. Edit `.env` file:

```bash
# Environment
ENV=development                    # development, staging, production

# Browser Configuration
BROWSER=chromium                   # chromium, firefox, webkit
HEADLESS=true                      # true or false
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080

# Execution Configuration
WORKERS=4                          # Parallel workers
DEFAULT_TIMEOUT=30000              # Timeout in milliseconds

# Reporting
SCREENSHOT_ON_FAILURE=true
VIDEO_MODE=retain-on-failure       # on, off, retain-on-failure
TRACE_MODE=retain-on-failure

# Logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
```

---

## 🏃 Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/login/test_login.py

# Run with verbose output
pytest -v

# Run with live output
pytest -s
```

### Run Tests by Markers

```bash
# Run only smoke tests
pytest -m smoke

# Run regression tests
pytest -m regression

# Run login tests
pytest -m login

# Run e2e tests
pytest -m e2e
```

### Parallel Execution

```bash
# Run with 4 parallel workers
pytest -n 4

# Run with auto-detected CPU count
pytest -n auto
```

### Browser Selection

```bash
# Run on Chromium (default)
pytest --browser=chromium

# Run on Firefox
pytest --browser=firefox

# Run on WebKit (Safari)
pytest --browser=webkit
```

### Generate Reports

```bash
# Generate HTML report
pytest --html=reports/report.html --self-contained-html

# Generate Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 🗂️ Test Organization

### Test Markers

| Marker | Description | Usage |
|--------|-------------|-------|
| `smoke` | Critical path tests | `pytest -m smoke` |
| `regression` | Full regression suite | `pytest -m regression` |
| `login` | Login/auth tests | `pytest -m login` |
| `products` | Product tests | `pytest -m products` |
| `cart` | Cart tests | `pytest -m cart` |
| `checkout` | Checkout tests | `pytest -m checkout` |
| `e2e` | End-to-end tests | `pytest -m e2e` |

---

## 📊 Reporting

### HTML Reports

```bash
pytest --html=reports/report.html --self-contained-html
```

### Allure Reports

```bash
# Generate results
pytest --alluredir=reports/allure-results

# Serve report (opens in browser)
allure serve reports/allure-results
```

### Logs

Logs are automatically generated:
- **Console logs**: Colored output during test execution
- **File logs**: Detailed logs saved to `logs/test_execution.log`

---

## 🔄 CI/CD Integration

### GitLab CI/CD

Complete configuration in `.gitlab-ci.yml`:
- Parallel test execution across multiple browsers
- Artifact collection (reports, logs, traces)
- Allure report generation
- Scheduled nightly runs

### GitHub Actions

Complete workflow in `.github/workflows/playwright-tests.yml`:
- Matrix testing (OS × Browser combinations)
- Artifact upload and retention
- GitHub Pages report deployment
- Automatic issue creation on failure

---

## 🎯 Best Practices

### Test Writing

1. **Use Page Objects**: Always interact through page objects
2. **Single Responsibility**: One test, one scenario
3. **Clear Test Names**: Descriptive names explaining what is tested
4. **Independent Tests**: Tests should not depend on each other
5. **Proper Assertions**: Use meaningful assertion messages

### Code Quality

1. **Type Hints**: Always add type annotations
2. **Docstrings**: Document all classes and functions
3. **Consistent Formatting**: Use Black and Ruff
4. **DRY Principle**: Don't Repeat Yourself
5. **Logging**: Log important actions and decisions

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Tests Fail with "Browser not found"

```bash
playwright install
playwright install-deps  # Linux only
```

#### 2. Timeout Errors

Increase timeouts in `.env`:

```bash
DEFAULT_TIMEOUT=60000
PAGE_LOAD_TIMEOUT=60000
```

#### 3. Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📝 License

This project is licensed under the MIT License.

---

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/python/docs/intro)
- [pytest Documentation](https://docs.pytest.org/)
- [Page Object Pattern](https://martinfowler.com/bliki/PageObject.html)

---

**Happy Testing! 🎭✨**
