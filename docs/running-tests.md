# Running Tests in Financed Sales

## Required Commands

### Run All Tests (Recommended)
```bash
bench --site dev.localhost run-tests --app financed_sales --skip-test-records
```

### Verbose Output
```bash
bench --site dev.localhost run-tests --app financed_sales --skip-test-records --verbose
```

### Generate XML Report
```bash
bench --site dev.localhost run-tests --app financed_sales --skip-test-records --junit-xml-output test_results.xml
```

### Run Specific Test
```bash
bench --site dev.localhost run-tests --app financed_sales --skip-test-records --test test_api
```

**Important**: Always use `--skip-test-records` - the tests are designed to work this way.

## Useful Options

| Option | Purpose |
|--------|---------|
| `--failfast` | Stop on first failure |
| `--profile` | Show performance profile |
| `--skip-test-records` | Skip test record creation (fixes dependency issues) |
