# Documentation Index

Welcome to the Python Trading Engine documentation! This directory contains comprehensive guides and references for developers and users.

## 📚 Table of Contents

### About This Documentation

- **[DOCS_ORGANIZATION.md](./DOCS_ORGANIZATION.md)** - How documentation is organized
  - Files moved to docs/
  - Updated references
  - Structure and benefits

### Getting Started

- **[QUICKSTART.md](./QUICKSTART.md)** - Get up and running in 5 minutes

  - Prerequisites check
  - Installation steps
  - First system test
  - Quick dev workflow

- **[MIGRATION.md](./MIGRATION.md)** - Migration guide for existing users
  - Old vs new structure comparison
  - File location mappings
  - Breaking changes
  - Migration checklist

### Development

- **[DEV_MODE.md](./DEV_MODE.md)** - Complete development mode guide

  - Mock data generator
  - Simulated traders
  - Configuration options
  - Troubleshooting
  - Best practices

- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
  - Complete folder structure
  - All created files
  - Design decisions
  - Architecture overview

### CLI Documentation

- **[CLI_GUIDE.md](./CLI_GUIDE.md)** - Complete CLI usage guide

  - All commands with examples
  - Visual improvements
  - Tips and tricks
  - Troubleshooting

- **[CLI_QUICK_REF.md](./CLI_QUICK_REF.md)** - Quick reference card

  - Command cheat sheet
  - Common workflows
  - Quick tips

- **[CLI_BEFORE_AFTER.md](./CLI_BEFORE_AFTER.md)** - CLI migration guide

  - Before/after comparison
  - Command structure changes
  - Visual improvements
  - Migration checklist

- **[CLI_ENHANCEMENT_SUMMARY.md](./CLI_ENHANCEMENT_SUMMARY.md)** - Technical CLI changes
  - Implementation details
  - Files modified
  - Benefits summary

## 🎯 Quick Links by Use Case

### I want to...

**Get started quickly**
→ [QUICKSTART.md](./QUICKSTART.md)

**Set up development environment**
→ [DEV_MODE.md](./DEV_MODE.md)

**Learn the CLI commands**
→ [CLI_GUIDE.md](./CLI_GUIDE.md) or [CLI_QUICK_REF.md](./CLI_QUICK_REF.md)

**Migrate from old structure**
→ [MIGRATION.md](./MIGRATION.md)

**Understand the architecture**
→ [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)

**See what changed with the CLI**
→ [CLI_BEFORE_AFTER.md](./CLI_BEFORE_AFTER.md)

## 📖 Additional Documentation

Component-specific documentation is located in the source tree:

- **Servers**: [src/servers/README.md](../src/servers/README.md)
- **Database**: [src/database/README.md](../src/database/README.md)
- **Frontend**: [src/frontend/README.md](../src/frontend/README.md)
- **Messaging**: [src/messaging/README.md](../src/messaging/README.md)
- **Shared**: [src/shared/README.md](../src/shared/README.md)

## 🚀 Recommended Reading Order

### For New Users

1. [QUICKSTART.md](./QUICKSTART.md) - Get the system running
2. [CLI_QUICK_REF.md](./CLI_QUICK_REF.md) - Learn basic commands
3. [DEV_MODE.md](./DEV_MODE.md) - Set up development tools
4. Component READMEs in `src/` - Understand the architecture

### For Developers

1. [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Architecture overview
2. [DEV_MODE.md](./DEV_MODE.md) - Development workflow
3. [CLI_GUIDE.md](./CLI_GUIDE.md) - Master the CLI
4. Component READMEs in `src/` - Deep dive into components

### For Migrating Users

1. [MIGRATION.md](./MIGRATION.md) - Understand what changed
2. [CLI_BEFORE_AFTER.md](./CLI_BEFORE_AFTER.md) - Update your workflows
3. [QUICKSTART.md](./QUICKSTART.md) - Test the new setup
4. [DEV_MODE.md](./DEV_MODE.md) - Explore new dev features

## 🔍 Finding Information

### By Topic

| Topic             | Document                                                 |
| ----------------- | -------------------------------------------------------- |
| Installation      | [QUICKSTART.md](./QUICKSTART.md)                         |
| CLI Commands      | [CLI_GUIDE.md](./CLI_GUIDE.md)                           |
| Development       | [DEV_MODE.md](./DEV_MODE.md)                             |
| Migration         | [MIGRATION.md](./MIGRATION.md)                           |
| Architecture      | [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) |
| Mock Data         | [DEV_MODE.md](./DEV_MODE.md)                             |
| Simulated Traders | [DEV_MODE.md](./DEV_MODE.md)                             |
| Servers (TES/OBS) | [../src/servers/README.md](../src/servers/README.md)     |
| Databases         | [../src/database/README.md](../src/database/README.md)   |
| Messaging         | [../src/messaging/README.md](../src/messaging/README.md) |

### By Component

| Component                   | Documentation                                            |
| --------------------------- | -------------------------------------------------------- |
| Trading Engine Server (TES) | [../src/servers/README.md](../src/servers/README.md)     |
| Order Book Server (OBS)     | [../src/servers/README.md](../src/servers/README.md)     |
| Transactional DB            | [../src/database/README.md](../src/database/README.md)   |
| Historical DB (KDB+)        | [../src/database/README.md](../src/database/README.md)   |
| Analytics DB                | [../src/database/README.md](../src/database/README.md)   |
| Utilities DB                | [../src/database/README.md](../src/database/README.md)   |
| Trader Portal               | [../src/frontend/README.md](../src/frontend/README.md)   |
| Analytics Dashboard         | [../src/frontend/README.md](../src/frontend/README.md)   |
| RabbitMQ Layer              | [../src/messaging/README.md](../src/messaging/README.md) |
| Shared Utilities            | [../src/shared/README.md](../src/shared/README.md)       |

## 💡 Tips

- **CLI Help**: Run `python main.py --help` for interactive help
- **Search**: Use your editor's search across all markdown files
- **Examples**: Most documents include practical examples
- **Updates**: Documentation is kept in sync with code changes

## 🤝 Contributing

When adding new features:

1. Update relevant documentation
2. Add examples to appropriate guides
3. Update this index if adding new documents
4. Keep component READMEs in their respective directories

## 📝 Documentation Style

- **User-facing docs**: Focus on "how to" and practical examples
- **Technical docs**: Include architecture decisions and implementation details
- **Quick references**: Brief, scannable format
- **Guides**: Step-by-step instructions with explanations

---

**Back to [Main README](../README.md)**
