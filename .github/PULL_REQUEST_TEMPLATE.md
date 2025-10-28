# Pull Request

## Description

<!-- Provide a clear and concise description of your changes -->

### Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test improvements
- [ ] CI/CD improvements
- [ ] Other (please describe):

## Motivation and Context

<!-- Why is this change required? What problem does it solve? -->
<!-- If it fixes an open issue, please link to the issue here -->

Fixes #(issue)
Related to #(issue)

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Testing

### Test Coverage

- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have maintained or improved test coverage

### Test Details

<!-- Describe the tests you ran and their results -->

```bash
# Command used to run tests
hatch run test:test

# Coverage results
hatch run test:cov
```

<!-- If applicable, describe manual testing performed -->

## Code Quality

### Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have run `hatch run lint:all` and fixed all issues
- [ ] I have run `hatch run lint:typing` and there are no type errors
- [ ] My code passes all pre-commit hooks
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

### Commit Messages

- [ ] My commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification
- [ ] Each commit is atomic and has a clear purpose

## Documentation

- [ ] I have updated the README (if needed)
- [ ] I have updated docstrings for modified functions/classes
- [ ] I have added/updated type hints
- [ ] I have updated CHANGELOG.md for user-facing changes
- [ ] I have added usage examples for new features

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->

- [ ] This PR introduces breaking changes
- [ ] I have updated the documentation to reflect breaking changes
- [ ] I have provided migration instructions

### Breaking Change Details

<!-- Describe what breaks and how users should adapt -->

## Performance Impact

<!-- If applicable, describe any performance implications -->

- [ ] This change improves performance
- [ ] This change has no performance impact
- [ ] This change may impact performance (details below)

### Performance Details

<!-- Provide benchmarks or performance analysis if applicable -->

## Dependencies

- [ ] This PR adds new dependencies
- [ ] All dependencies are compatible with Python 3.9+

### New Dependencies

<!-- List any new dependencies and justify their addition -->

## Screenshots

<!-- If applicable, add screenshots to help explain your changes -->

## Checklist

### Before Requesting Review

- [ ] I have performed a self-review of my own code
- [ ] I have tested my changes locally
- [ ] I have checked that my changes don't break existing functionality
- [ ] I have rebased onto the latest `main` branch
- [ ] I have resolved all merge conflicts

### Reviewer Notes

<!-- Any specific areas you'd like reviewers to focus on? -->

## Additional Notes

<!-- Any additional information that reviewers should know -->

---

## For Maintainers

<!-- Maintainers can use this section during review -->

### Review Checklist

- [ ] Code quality is acceptable
- [ ] Tests are comprehensive and pass
- [ ] Documentation is adequate
- [ ] Breaking changes are documented
- [ ] CHANGELOG is updated
- [ ] Ready to merge
