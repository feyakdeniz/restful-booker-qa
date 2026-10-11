# Restful-Booker API – Test Findings

**Tester:** Feyzanur Akdeniz
**System under test:** [Restful-Booker](https://restful-booker.herokuapp.com) – a hotel booking API built for API testing practice
**Tool:** Postman
**Date:** 8 October 2026

---

## Test execution

End-to-end booking flow tested manually in Postman:

| # | Test | Request | Expected | Actual | Result |
|---|---|---|---|---|---|
| 1 | List all bookings | `GET /booking` | 200, list of booking IDs | 200, list of booking IDs | ✅ Pass |
| 2 | Get a booking by ID | `GET /booking/{id}` | 200, booking details | 200, booking details | ✅ Pass |
| 3 | Get token with valid credentials | `POST /auth` | 200, token | 200, token | ✅ Pass |
| 4 | Get token with invalid password | `POST /auth` | 401 | 200 + "Bad credentials" | ❌ Fail (BUG-01) |
| 5 | Create a booking | `POST /booking` | 201, booking ID | 200, booking ID | ❌ Fail (BUG-02) |
| 6 | Read the created booking | `GET /booking/{id}` | 200, same data as sent | 200, same data as sent | ✅ Pass |
| 7 | Update booking with token | `PUT /booking/{id}` | 200, updated data | 200, updated data | ✅ Pass |
| 8 | Update booking without token | `PUT /booking/{id}` | 401, not updated | 403, not updated | ❌ Fail (BUG-03) |
| 9 | Delete booking with token | `DELETE /booking/{id}` | 204 / 200 | 201 | ❌ Fail (BUG-04) |
| 10 | Read the deleted booking | `GET /booking/{id}` | 404 | 404 | ✅ Pass |

**Note:** The public test environment resets its data periodically. A booking created a few minutes earlier returned 404; after checking the request, the booking was recreated and verified immediately. This was an environment behaviour, not a defect.

---

## Summary

| ID | Title | Severity | Priority | Status |
|---|---|---|---|---|
| BUG-01 | Login with invalid credentials returns `200 OK` instead of `401` | High | High | Open |
| BUG-02 | Creating a booking returns `200 OK` instead of `201 Created` | Low | Low | Open |
| BUG-03 | Updating a booking without a token returns `403` instead of `401` | Low | Low | Open |
| BUG-04 | Deleting a booking returns `201 Created` instead of `204`/`200` | Low | Low | Open |

---

## BUG-01 – Login with invalid credentials returns `200 OK` instead of `401 Unauthorized`

| Field | Details |
|---|---|
| **Endpoint** | `POST /auth` |
| **Environment** | https://restful-booker.herokuapp.com |
| **Severity / Priority** | High / High |

**Steps to reproduce**
1. Send `POST https://restful-booker.herokuapp.com/auth`
2. Header: `Content-Type: application/json`
3. Body:
   ```json
   {
       "username": "admin",
       "password": "yanlis123"
   }
   ```

**Expected result**
Status `401 Unauthorized` with an error message.

**Actual result**
Status `200 OK` with body `{"reason": "Bad credentials"}`.

**Impact**
A failed login is reported with a success status code. Any client that relies on the status code (which is the standard practice) may treat the user as logged in. It also makes monitoring and automated tests unable to detect failed logins by status code alone.

---

## BUG-02 – Creating a booking returns `200 OK` instead of `201 Created`

| Field | Details |
|---|---|
| **Endpoint** | `POST /booking` |
| **Environment** | https://restful-booker.herokuapp.com |
| **Severity / Priority** | Low / Low |

**Steps to reproduce**
1. Send `POST https://restful-booker.herokuapp.com/booking`
2. Headers: `Content-Type: application/json`, `Accept: application/json`
3. Body:
   ```json
   {
       "firstname": "Feyza",
       "lastname": "Akdeniz",
       "totalprice": 250,
       "depositpaid": true,
       "bookingdates": {
           "checkin": "2026-11-10",
           "checkout": "2026-11-12"
       },
       "additionalneeds": "Breakfast"
   }
   ```

**Expected result**
Status `201 Created`, since a new resource is created.

**Actual result**
Status `200 OK`. The booking is created successfully (booking ID returned).

**Impact**
Functionality works, but the response does not follow REST conventions. Low risk; clients expecting `201` may need special handling.

---

## BUG-03 – Updating a booking without a token returns `403 Forbidden` instead of `401 Unauthorized`

| Field | Details |
|---|---|
| **Endpoint** | `PUT /booking/{id}` |
| **Environment** | https://restful-booker.herokuapp.com |
| **Severity / Priority** | Low / Low |

**Steps to reproduce**
1. Create a booking with `POST /booking` and note the `bookingid`
2. Send `PUT https://restful-booker.herokuapp.com/booking/{bookingid}` with a valid JSON body
3. Do **not** include the `Cookie: token=...` header

**Expected result**
Status `401 Unauthorized`: the request has no credentials, so the client is not authenticated.

**Actual result**
Status `403 Forbidden`. The update is correctly rejected and the booking is not changed.

**Impact**
Security behaviour is correct (unauthenticated users cannot modify bookings), but the status code is misleading. `403` means "authenticated but not allowed", so clients cannot tell whether they need to log in or simply lack permission.

---

## BUG-04 – Deleting a booking returns `201 Created` instead of `204 No Content` / `200 OK`

| Field | Details |
|---|---|
| **Endpoint** | `DELETE /booking/{id}` |
| **Environment** | https://restful-booker.herokuapp.com |
| **Severity / Priority** | Low / Low |

**Steps to reproduce**
1. Get a token with `POST /auth`
2. Create a booking with `POST /booking` and note the `bookingid`
3. Send `DELETE https://restful-booker.herokuapp.com/booking/{bookingid}` with header `Cookie: token={token}`

**Expected result**
Status `204 No Content` (or `200 OK`): the resource was deleted.

**Actual result**
Status `201 Created`.

**Impact**
The deletion itself works, but `201` means a new resource was created, the opposite of what happened. This is misleading for client applications and for anyone reading logs or monitoring dashboards.

---

## Observation (needs clarification)

**OBS-01 – Existing booking with inconsistent data**
Booking `GET /booking/12` contained a one-year stay (`2018-01-01` → `2019-01-01`) with a total price of `111`.
This may indicate missing validation (maximum stay length, price consistent with number of nights), **or** a gap in the specification. To be clarified with the analyst before logging as a bug.
