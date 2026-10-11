# Restful-Booker API Testing

[![API tests](https://github.com/feyakdeniz/restful-booker-qa/actions/workflows/api-tests.yml/badge.svg)](https://github.com/feyakdeniz/restful-booker-qa/actions/workflows/api-tests.yml)

API testing project for [Restful-Booker](https://restful-booker.herokuapp.com), a public hotel booking API built for testers to practise on.

**Author:** Feyzanur Akdeniz

## What this project covers

- **Manual exploratory testing** of the booking API in Postman: positive and negative scenarios
- **Bug reports** for the issues found, with steps to reproduce, expected and actual results, and severity
- **Automated regression suite in Postman:** 7 requests, 14 tests, running the full booking lifecycle end to end
- **Automated test suite in Python + pytest:** 7 independent tests using fixtures for setup and teardown
- **CI with GitHub Actions:** both suites run on every push, on pull requests and every night

## Project structure

```
├── tests/
│   ├── conftest.py        # fixtures: base URL, auth token, test booking (setup/teardown)
│   └── test_booking.py    # positive and negative API tests
├── postman/
│   └── Restful-Booker_Tests.postman_collection.json
├── .github/workflows/
│   └── api-tests.yml      # CI pipeline: pytest + Newman
├── BUG_REPORTS.md         # bugs found, with steps to reproduce
└── requirements.txt
```

## Test scope

| Area | Endpoint | What is checked |
|---|---|---|
| Health / listing | `GET /booking` | Status code, non-empty list, schema (`bookingid` is a number), response time |
| Authentication | `POST /auth` | Token is returned and stored for later requests |
| Create | `POST /booking` | Booking is created, response data matches the request, ID is stored |
| Read | `GET /booking/{id}` | Data read back matches what was created |
| Update | `PUT /booking/{id}` | Changes are applied (requires token) |
| Delete | `DELETE /booking/{id}` | Booking is deleted (requires token) |
| Verify delete | `GET /booking/{id}` | Deleted booking returns `404` |

Negative tests: login with a wrong password, and updating a booking without a token (the booking must stay unchanged).

### Design decisions

- **Independent tests (pytest):** a `booking` fixture creates a fresh booking before each test and deletes it afterwards, even if the test fails. Tests do not depend on each other or on their order, which avoids a common cause of flaky tests.
- **Chained requests (Postman):** the auth token and the booking ID are saved as collection variables and reused by later requests. Requests are ordered by their dependencies, and each run creates and deletes its own data.
- **Verify, don't trust:** after creating or updating a booking, the tests read it back to confirm the change was really saved.
- **Known bugs:** where the API returns a non-standard status code, the test accepts the current behaviour and references the bug ID. BUG-01 has its own test marked `xfail(strict=True)`: it is reported as an expected failure today, and pytest will flag it as soon as the bug is fixed so the marker can be removed.
- **Configurable environment:** the API address is read from the `BASE_URL` environment variable, so the same tests can run against another environment without code changes.

## Findings

4 bugs and 1 observation. Full reports in [BUG_REPORTS.md](BUG_REPORTS.md).

| ID | Title | Severity |
|---|---|---|
| BUG-01 | Login with invalid credentials returns `200 OK` instead of `401` | High |
| BUG-02 | Creating a booking returns `200 OK` instead of `201 Created` | Low |
| BUG-03 | Updating without a token returns `403` instead of `401` | Low |
| BUG-04 | Deleting a booking returns `201 Created` instead of `204`/`200` | Low |

## How to run

### Python + pytest
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```
Expected result: `6 passed, 1 xfailed` (the xfail is BUG-01).

### In Postman
1. Import `postman/Restful-Booker_Tests.postman_collection.json`
2. Open the collection → **Run** → **Run Restful-Booker Tests**

### From the command line (Newman)
```bash
npm install -g newman
newman run postman/Restful-Booker_Tests.postman_collection.json
```

> **Note:** Restful-Booker is a shared public environment that resets its data periodically, so occasional failures caused by the environment are possible.
