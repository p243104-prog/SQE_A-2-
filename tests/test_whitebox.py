import pytest

from registration import (
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course,
    Student,
    Course,
)


# White-box tests for check_credit_limit()

def test_credit_limit_valid():
    assert check_credit_limit(10, 4) is True


def test_credit_limit_exactly_18():
    assert check_credit_limit(14, 4) is True


def test_credit_limit_exceeded():
    assert check_credit_limit(15, 4) is False


def test_invalid_current_credits():
    import pytest

    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(-1, 3)


def test_invalid_course_credits():
    import pytest

    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(10, 5)

# White-box tests for prerequisites_satisfied()

def test_no_prerequisites_required():
    assert prerequisites_satisfied(set(), set()) is True


def test_all_prerequisites_completed():
    completed = {"CS101", "CS102"}
    required = {"CS101", "CS102"}

    assert prerequisites_satisfied(completed, required) is True


def test_one_prerequisite_missing():
    completed = {"CS101"}
    required = {"CS101", "CS102"}

    assert prerequisites_satisfied(completed, required) is False


def test_no_prerequisites_completed():
    completed = set()
    required = {"CS101", "CS102"}

    assert prerequisites_satisfied(completed, required) is False

# White-box tests for registration_decision()

def test_registration_with_available_seat():
    student = Student(student_id="S001")
    course = Course(code="CS201", credit_hours=3, capacity=30, enrolled=10)

    assert registration_decision(student, course) == "REGISTERED"


def test_registration_blocked_by_one_rupee_dues():
    student = Student(student_id="S002", outstanding_dues=1)
    course = Course(code="CS202", credit_hours=3, capacity=30, enrolled=10)

    assert registration_decision(student, course) == "DUES_BLOCK"


def test_registration_when_course_is_full():
    student = Student(student_id="S003")
    course = Course(code="CS203", credit_hours=3, capacity=30, enrolled=30)

    assert registration_decision(student, course) == "WAITLISTED"


def test_registration_exceeds_credit_limit():
    student = Student(student_id="S004", current_credits=16)
    course = Course(code="CS204", credit_hours=3, capacity=30, enrolled=10)

    assert registration_decision(student, course) == "CREDIT_LIMIT"


def test_registration_decision_does_not_modify_objects():
    student = Student(student_id="S005")
    course = Course(code="CS205", credit_hours=3, capacity=30, enrolled=10)

    original_credits = student.current_credits
    original_registered = student.registered_courses.copy()
    original_enrolled = course.enrolled

    registration_decision(student, course)

    assert student.current_credits == original_credits
    assert student.registered_courses == original_registered
    assert course.enrolled == original_enrolled

# White-box tests for register_course()

def test_successful_registration_updates_records():
    student = Student(student_id="S006")
    course = Course(code="CS301", credit_hours=3, capacity=30, enrolled=10)

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS301" in student.registered_courses
    assert student.current_credits == 3
    assert course.enrolled == 11


def test_failed_registration_does_not_update_records():
    student = Student(student_id="S007", outstanding_dues=1)
    course = Course(code="CS302", credit_hours=3, capacity=30, enrolled=10)

    result = register_course(student, course)

    assert result == "DUES_BLOCK"
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 10


# White-box tests for withdraw_course()

def test_successful_withdrawal_updates_records():
    student = Student(
        student_id="S008",
        current_credits=3,
        registered_courses={"CS303"}
    )
    course = Course(code="CS303", credit_hours=3, capacity=30, enrolled=10)

    result = withdraw_course(student, course)

    assert result is True
    assert "CS303" not in student.registered_courses
    assert student.current_credits == 0
    assert course.enrolled == 9


def test_withdrawal_when_not_registered():
    student = Student(student_id="S009")
    course = Course(code="CS304", credit_hours=3, capacity=30, enrolled=10)

    result = withdraw_course(student, course)

    assert result is False
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 10


def test_negative_dues_raises_error():
    student = Student("S101", outstanding_dues=-1)
    course = Course("CS101", 3, 30)

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


def test_invalid_course_capacity_raises_error():
    student = Student("S102")
    course = Course("CS101", 3, 0)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_enrollment_greater_than_capacity_raises_error():
    student = Student("S103")
    course = Course("CS101", 3, 30, enrolled=31)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_already_registered():
    student = Student("S104", registered_courses={"CS101"})
    course = Course("CS101", 3, 30)

    result = registration_decision(student, course)

    assert result == "ALREADY_REGISTERED"


def test_missing_prerequisite():
    student = Student("S105", completed_courses=set())
    course = Course("CS201", 3, 30, prerequisites={"CS101"})

    result = registration_decision(student, course)

    assert result == "PREREQUISITES_MISSING"


def test_waitlist_student_added_only_once():
    student = Student("S106")
    course = Course("CS101", 3, 30, enrolled=30)

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert course.waitlist == ["S106"]


def test_existing_waitlist_student_not_added_again():
    student = Student("S107")
    course = Course(
        "CS101",
        3,
        30,
        enrolled=30,
        waitlist=["S107"]
    )

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert course.waitlist == ["S107"]

def test_dues_above_1000_triggers_dues_block():
    student = Student("S108", outstanding_dues=1001)
    course = Course("CS101", 3, 30)

    result = registration_decision(student, course)

    assert result == "DUES_BLOCK"
