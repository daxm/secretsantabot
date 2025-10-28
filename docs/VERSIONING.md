# Versioning Scheme

## Format

`<major>.<yyyymmdd>.<patch>`

## Components

- **major**: Major version (breaking changes, major rewrites)
- **yyyymmdd**: Date of release (e.g., 20251028)
- **patch**: Patch number for that day (starts at 0)

## Examples

- `1.20251028.0` - First release on October 28, 2025
- `1.20251028.1` - First patch on October 28, 2025
- `2.20260115.0` - Major version 2, released January 15, 2026

## Incrementing Rules

### Patch (third number)
- Bug fixes
- Minor improvements
- Documentation updates
- No breaking changes

### Date (middle number)
- New features
- Enhancements
- Non-breaking changes
- Reset patch to 0

### Major (first number)
- Breaking API changes
- Major architectural changes
- Database schema breaking changes
- Reset date and patch

## Where Version is Stored

- `pyproject.toml` - Primary source
- `VERSION` - Simple text file for scripts
- Both must be kept in sync

## Updating Version

1. Update `pyproject.toml` version field
2. Update `VERSION` file
3. Commit both changes together
4. Tag release in git: `git tag v1.20251028.0`
