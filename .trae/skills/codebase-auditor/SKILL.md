---
name: "codebase-auditor"
description: "Performs systematic codebase audits for quality, security, and performance. Invoke when user wants comprehensive code review, before major releases, or when fixing technical debt."
---

# Codebase Auditor Skill

This skill provides systematic auditing capabilities for comprehensive codebase analysis and improvement.

## Audit Categories

### 1. Code Quality & Standards
- Code style consistency (PEP 8, naming conventions)
- Documentation completeness
- Comment quality and coverage
- Module organization and structure

### 2. Security Analysis  
- Vulnerability detection (SQL injection, XSS, etc.)
- Authentication and authorization checks
- Input validation and sanitization
- Secret management and hardcoded credentials

### 3. Performance Optimization
- Algorithm complexity analysis
- Database query optimization
- Memory usage and leaks
- I/O operations efficiency

### 4. Testing & Reliability
- Test coverage analysis
- Mock usage and test isolation
- Error handling robustness
- Edge case coverage

### 5. Architecture & Design
- Component coupling and cohesion
- Design pattern implementation
- API design consistency
- Scalability considerations

## Usage

Invoke this skill when:
- Preparing for major releases
- Addressing technical debt
- Onboarding new team members  
- After significant refactoring
- When performance issues arise
- For security compliance reviews

## Audit Process

1. **Static Analysis**: Automated code scanning
2. **Manual Review**: Expert pattern recognition
3. **Metrics Collection**: Quantitative quality measures
4. **Recommendations**: Actionable improvement suggestions
5. **Priority Ranking**: Critical → High → Medium → Low

## Output Format

- **Summary Report**: High-level findings and metrics
- **Detailed Findings**: File-by-file analysis with line numbers
- **Action Items**: Specific fixes with estimated effort
- **Risk Assessment**: Security and stability impact ratings