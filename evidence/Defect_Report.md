# White-Box Testing Defect Report

## 1. Introduction

This document records the defects identified during white-box testing of the Student Course Registration System.

The defects were identified by comparing the original implementation of `registration.py` against the expected behavior defined in `REQUIREMENTS.md`.

## 2. Defect Summary

| Defect ID | Defect Title | Severity | Status |
|---|---|---|---|
| D-01 | Incorrect Credit Limit Validation | High | Open |
| D-02 | Incorrect Prerequisite Validation | High | Open |
| D-03 | Incorrect Outstanding Dues Validation | High | Open |
| D-04 | Incorrect Waitlist Condition | High | Open |
| D-05 | Missing Enrollment Update During Withdrawal | Medium | Open |

## 3. Detailed Defect Reports

### D-01: Incorrect Credit Limit Validation

**Severity:** High

**Affected Function:** `check_credit_limit()`

**Requirement:** FR-01

**Description:**

The implementation uses a strict less-than comparison (`< 18`) instead of allowing a total credit load equal to 18.

**Steps to Reproduce:**

1. Call `check_credit_limit(14, 4)`.
2. Observe the returned result.

**Expected Result:**

The function should return `True` because the total is exactly 18 credits.

**Actual Result:**

The function returns `False`.

**Evidence:** `test_credit_limit_exactly_18`

### D-02: Incorrect Prerequisite Validation

**Severity:** High

**Affected Function:** `prerequisites_satisfied()`

**Requirement:** FR-03

**Description:**

The implementation uses set intersection and returns `True` when at least one prerequisite is completed. The requirement states that all required prerequisites must be completed.

**Steps to Reproduce:**

1. Provide completed courses: `{"CS101"}`.
2. Provide required courses: `{"CS101", "CS102"}`.
3. Check the returned result.

**Expected Result:**

The function should return `False` because CS102 is missing.

**Actual Result:**

The function returns `True`.

**Evidence:** `test_one_prerequisite_missing`

### D-03: Incorrect Outstanding Dues Validation

**Severity:** High

**Affected Function:** `registration_decision()`

**Requirement:** FR-04

**Description:**

The implementation blocks registration only when outstanding dues exceed 1000. The requirement states that any positive dues balance must block registration.

**Steps to Reproduce:**

1. Create a student with outstanding dues of 1.
2. Attempt to register the student in an otherwise eligible course.
3. Observe the registration result.

**Expected Result:**

`DUES_BLOCK`

**Actual Result:**

`REGISTERED`

**Evidence:**
- `test_registration_blocked_by_one_rupee_dues`
- `test_failed_registration_does_not_update_records`

### D-04: Incorrect Waitlist Condition

**Severity:** High

**Affected Function:** `registration_decision()`

**Requirement:** FR-08

**Description:**

The implementation checks whether enrolled students are greater than the course capacity instead of checking whether enrollment has reached capacity.

Additionally, the earlier validation rejects enrollment greater than capacity. Therefore, the WAITLISTED branch cannot be reached through valid inputs.

**Steps to Reproduce:**

1. Create a course with capacity 30 and enrolled students 30.
2. Create an otherwise eligible student.
3. Call `registration_decision()`.

**Expected Result:**

`WAITLISTED`

**Actual Result:**

`REGISTERED`

**Evidence:**
- `test_registration_when_course_is_full`
- `test_waitlist_student_added_only_once`
- `test_existing_waitlist_student_not_added_again`

### D-05: Missing Enrollment Update During Withdrawal

**Severity:** Medium

**Affected Function:** `withdraw_course()`

**Requirement:** FR-13

**Description:**

When a student withdraws from a course, the implementation removes the course from the student's registered courses and subtracts the credit hours. However, it does not decrement the course enrollment count.

**Steps to Reproduce:**

1. Create a student registered in CS101.
2. Set the student's current credits to 3.
3. Set the course enrollment count to 1.
4. Withdraw the student from the course.
5. Check the student's and course's records.

**Expected Result:**

- The course should be removed from the student's registered courses.
- Student credits should decrease by 3.
- Course enrollment should decrease from 1 to 0.

**Actual Result:**

Course enrollment remains 1.

**Evidence:** `test_successful_withdrawal_updates_records`

## 4. Overall Defect Summary

A total of five distinct defect areas were identified during white-box testing.

| Metric | Result |
|---|---:|
| Total distinct defect areas | 5 |
| High severity | 4 |
| Medium severity | 1 |
| Open defects | 5 |

## 5. Conclusion

White-box testing identified five distinct defects in the original Student Course Registration System.

These defects affect credit validation, prerequisite checking, outstanding dues, course waitlisting, and withdrawal processing.

The defects are documented with reproducible steps, expected results, actual results, and associated test evidence.

The original source code remains unchanged during baseline testing.
