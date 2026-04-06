# Dependabot Configuration

This document explains the Dependabot setup for automatic dependency management in EcoRoute Atlas.

## Overview

Dependabot automatically creates pull requests to update dependencies on a weekly schedule. This helps keep the project secure and up-to-date with the latest bug fixes and features.

## Configuration File

Location: `.github/dependabot.yml`

### Monitored Ecosystems

1. **Python Dependencies (pip)**
   - Checks `pyproject.toml` for Python package updates
   - Weekly checks on Mondays at 09:00 UTC
   - Maximum 10 open PRs at a time
   - Labeled with `dependencies` and `python`

2. **Docker Dependencies**
   - Checks `Dockerfile` for base image updates
   - Weekly checks on Mondays at 09:00 UTC
   - Maximum 5 open PRs at a time
   - Labeled with `dependencies` and `docker`

3. **GitHub Actions**
   - Checks workflow files for Action updates
   - Weekly checks on Mondays at 09:00 UTC
   - Maximum 5 open PRs at a time
   - Labeled with `dependencies` and `github-actions`

### Version Update Strategy

- **Direct & Indirect Dependencies**: Both types are monitored
- **Protected Major Updates**: Major version updates are ignored for:
  - `fastapi`
  - `pydantic`
  - `sqlalchemy`

This prevents breaking changes from being auto-merged. These should be updated manually when needed.

### Pull Request Settings

- **Assignees**: All PRs are assigned to `shahadathhs`
- **Reviewers**: All PRs request review from `shahadathhs`
- **Commit Message Prefixes**:
  - Python deps: `deps` or `deps-dev`
  - Docker: `docker`
  - GitHub Actions: `ci`

## Workflow

### Automatic Process

1. Dependabot checks for updates every Monday at 09:00 UTC
2. Creates PRs for outdated dependencies
3. Assigns and requests review from maintainer
4. PRs include:
   - Version change details
   - Release notes (when available)
   - Security advisories (if applicable)

### Manual Review Process

1. Review the Dependabot PR
2. Check for breaking changes in release notes
3. Run local tests:
   ```bash
   make pre-commit-run
   make check-all
   ```
4. If tests pass, merge the PR
5. If tests fail:
   - Investigate the breaking change
   - Update code as needed
   - Or close the PR to skip that version

### Security Updates

Dependabot will immediately create PRs for:
- Vulnerabilities in dependencies
- Security advisories
- Critical patches

These bypass the weekly schedule and should be prioritized.

## Customization

### Adjust Schedule

To change the check frequency or time, edit `.github/dependabot.yml`:

```yaml
schedule:
  interval: "daily"  # or "weekly", "monthly"
  time: "09:00"      # UTC time
  day: "monday"      # for weekly: day of week
  day: 1             # for monthly: day of month
```

### Ignore Specific Versions

To ignore specific versions or ranges:

```yaml
ignore:
  - dependency-name: "package-name"
    versions: ["2.x", "3.0.0"]
```

### Add More Reviewers

To add more team members to review PRs:

```yaml
reviewers:
  - "shahadathhs"
  - "other-maintainer"
```

### Limit Open PRs

To reduce the maximum number of open PRs:

```yaml
open-pull-requests-limit: 5  # Default is 10 for pip, 5 for others
```

## Best Practices

1. **Review PRs Promptly**: Don't let Dependabot PRs accumulate
2. **Test Before Merging**: Always run tests, especially for major updates
3. **Check Release Notes**: Look for breaking changes
4. **Update Documentation**: If a dependency changes behavior significantly
5. **Monitor Security Alerts**: Prioritize security updates
6. **Keep Protected Updates Updated**: Periodically review if major version blocks can be lifted

## Troubleshooting

### Dependabot Not Working

1. Check that Dependabot is enabled in repository settings
2. Verify `.github/dependabot.yml` syntax is correct
3. Check GitHub Actions logs for errors
4. Ensure repository has Dependabot access

### Too Many PRs

Reduce `open-pull-requests-limit` or change schedule to `monthly` instead of `weekly`.

### Breaking Changes

1. Add the dependency to the `ignore` list with specific version constraints
2. Or update the code to work with the new version
3. Document the breaking change in CHANGELOG.md

### False Positives

If Dependabot reports an issue that isn't actually a problem:

1. Check if it's a transitive dependency issue
2. Review the security advisory details
3. Update to a version that resolves the issue

## Related Documentation

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [CLAUDE.md](../CLAUDE.md) - Project development guide
- [pyproject.toml](../pyproject.toml) - Python dependencies

## Maintenance

This configuration should be reviewed:
- When adding new package ecosystems
- When changing team structure (reviewers/assignees)
- When project update requirements change
- Annually to ensure version ignore rules are still relevant

---

**Last Updated**: 2026-04-06
**Maintainer**: @shahadathhs
