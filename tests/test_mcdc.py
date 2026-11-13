
"""MC/DC tests for the capacity validation decision."""

import pytest

from registration import Student, Course, registration_decision


def test_mcdc_tc01_invalid_enrollment():
    """Condition A is True and Condition B is False."""
    student = Student(student_id="S001")
    course = Course(
        code="CS101",
        credit_hours=3,
        capacity=30,
        enrolled=31
    )

    with pytest.raises(
        ValueError,
        match="Invalid capacity or enrollment"
    ):
        registration_decision(student, course)


def test_mcdc_tc02_both_conditions_false():
    """Condition A is False and Condition B is False."""
    student = Student(student_id="S002")
    course = Course(
        code="CS102",
        credit_hours=3,
        capacity=1,
        enrolled=0
    )

    result = registration_decision(student, course)

    assert result == "REGISTERED"


def test_mcdc_tc03_invalid_capacity():
    """Condition A is False and Condition B is True."""
    student = Student(student_id="S003")
    course = Course(
        code="CS103",
        credit_hours=3,
        capacity=0,
        enrolled=0
    )

    with pytest.raises(
        ValueError,
        match="Invalid capacity or enrollment"
    ):
        registration_decision(student, course)
