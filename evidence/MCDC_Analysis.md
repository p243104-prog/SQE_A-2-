# Modified Condition/Decision Coverage (MC/DC) Analysis

## 1. Introduction

Modified Condition/Decision Coverage (MC/DC) is a white-box testing technique. It verifies that every individual Boolean condition can independently affect the overall decision outcome.

In this assignment, MC/DC analysis is performed on the compound Boolean condition inside the `registration_decision()` function.

## 2. Compound Boolean Expression

The selected source-code condition is:

```python
if not 0 <= course.enrolled <= course.capacity or course.capacity < 1:
```

The expression contains two individual conditions:

- **Condition A:** `not (0 <= course.enrolled <= course.capacity)`
- **Condition B:** `course.capacity < 1`

The complete decision is:

`D = A OR B`

The decision becomes TRUE if at least one condition is TRUE.

## 3. MC/DC Test Cases

Three test cases are designed to demonstrate the independent effect of each condition.

| Test Case | Enrolled | Capacity | A | B | Decision (A OR B) |
|---|---:|---:|---|---|---|
| TC-01 | 31 | 30 | T | F | T |
| TC-02 | 0 | 1 | F | F | F |
| TC-03 | 0 | 0 | F | T | T |

T = True, F = False.

## 4. Independent Effect Analysis

### Condition A

Compare TC-01 and TC-02:

- Condition A changes from TRUE to FALSE.
- Condition B remains FALSE.
- The overall decision changes from TRUE to FALSE.

Therefore, Condition A independently affects the decision outcome.

### Condition B

Compare TC-02 and TC-03:

- Condition A remains FALSE.
- Condition B changes from FALSE to TRUE.
- The overall decision changes from FALSE to TRUE.

Therefore, Condition B independently affects the decision outcome.

## 5. Test Input Details and Expected Results

| Test Case | Course Enrollment | Expected Result |
|---|---|---|
| TC-01 | Enrolled = 31, Capacity = 30 | ValueError: Invalid capacity or enrollment |
| TC-02 | Enrolled = 0, Capacity = 1 | Registration continues and returns REGISTERED for an otherwise eligible student |
| TC-03 | Enrolled = 0, Capacity = 0 | ValueError: Invalid capacity or enrollment |

For TC-02, the student must have no outstanding dues, no duplicate registration, satisfied prerequisites, and sufficient credit allowance.

## 6. MC/DC Coverage Result

Both individual conditions have been demonstrated to independently affect the overall decision.

| Condition | Independent Effect Demonstrated |
|---|---|
| Condition A | Yes |
| Condition B | Yes |

**MC/DC result: 100% logical condition/decision independence demonstrated for this compound expression.**

Note: Python uses short-circuit evaluation for OR. When Condition A is TRUE, Condition B is not actually evaluated. Its FALSE value in TC-01 is established from the test input. This should be considered when interpreting tool-measured condition coverage.

## 7. Conclusion

MC/DC analysis was performed on the compound capacity-validation expression in `registration_decision()`.

Three test cases were designed to demonstrate the independent effect of both Boolean conditions on the overall decision.

The analysis provides additional evidence that the capacity-validation logic has been examined at the individual condition level.


## 8. Actual Test Execution Results

The three designed MC/DC test cases were implemented in
`tests/test_mcdc.py` and executed using pytest.

Execution command:

`python -m pytest -v tests/test_mcdc.py`

Result:

- Total test cases: 3
- Passed: 3
- Failed: 0

The execution evidence is saved in:

`evidence/mcdc-execution.txt`

All three test cases produced their expected results.
