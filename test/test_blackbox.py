import pytest
from registration import (
    Student,
    Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course,
)


def make_student(sid="S001", completed=None, credits=0, dues=0, registered=None):
    return Student(
        student_id=sid,
        completed_courses=set(completed or []),
        current_credits=credits,
        outstanding_dues=dues,
        registered_courses=set(registered or []),
    )


def make_course(code="CS201", credits=3, capacity=30, enrolled=0, prereqs=None):
    return Course(
        code=code,
        credit_hours=credits,
        capacity=capacity,
        enrolled=enrolled,
        prerequisites=set(prereqs or []),
    )


class TestECP:
    """Equivalence class partitioning cases (valid + invalid classes)."""

    # --- check_credit_limit — FR-01 / FR-02 ---
    def test_ecp_credit_limit_valid_class(self):
        """ECP/FR-01 | Valid class: current in [0,18], new in [1,4], sum<=18 -> True"""
        assert check_credit_limit(0, 1) is True
        assert check_credit_limit(15, 3) is True

    def test_ecp_credit_limit_exceeded_class(self):
        """ECP/FR-01 | Valid-args but exceeds: current=17,new=3 -> False"""
        assert check_credit_limit(17, 3) is False

    def test_ecp_credit_limit_invalid_current(self):
        """ECP/FR-02 | Invalid current (<0 or >18) -> ValueError"""
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(-1, 3)
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(19, 3)

    def test_ecp_credit_limit_invalid_new(self):
        """ECP/FR-02 | Invalid new_credits (<1 or >4) -> ValueError"""
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(10, 0)
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(10, 5)

    # --- prerequisites_satisfied — FR-03 ---
    def test_ecp_prereq_none_required(self):
        """ECP/FR-03 | Empty required -> True"""
        assert prerequisites_satisfied(set(), set()) is True
        assert prerequisites_satisfied({"CS101"}, set()) is True

    def test_ecp_prereq_all_completed(self):
        """ECP/FR-03 | All completed -> True"""
        assert prerequisites_satisfied({"CS101", "MATH101"},
                                       {"CS101", "MATH101"}) is True

    def test_ecp_prereq_some_completed(self):
        """ECP/FR-03 | Only some completed -> False (per SRS, needs ALL)"""
        assert prerequisites_satisfied({"CS101"}, {"CS101", "MATH101"}) is False

    # --- dues ECP — FR-04 ---
    def test_ecp_dues_zero_registers(self):
        """ECP/FR-04 | Dues = 0 (valid class) -> REGISTERED"""
        s = make_student(dues=0)
        c = make_course()
        assert registration_decision(s, c) == "REGISTERED"

    def test_ecp_dues_positive_blocks(self):
        """ECP/FR-04 | Dues > 0 (invalid class) -> DUES_BLOCK"""
        s = make_student(dues=1)
        c = make_course()
        assert registration_decision(s, c) == "DUES_BLOCK"

    def test_ecp_dues_negative_raises(self):
        """ECP/FR-15 | Dues < 0 -> ValueError"""
        s = make_student(dues=-1)
        c = make_course()
        with pytest.raises(ValueError, match="Invalid dues"):
            registration_decision(s, c)

    # --- availability ECP — FR-08 ---
    def test_ecp_availability_seats_available(self):
        """ECP/FR-08 | enrolled < capacity -> REGISTERED"""
        s = make_student()
        c = make_course(capacity=30, enrolled=0)
        assert registration_decision(s, c) == "REGISTERED"

    def test_ecp_availability_full(self):
        """ECP/FR-08 | enrolled == capacity -> WAITLISTED"""
        s = make_student()
        c = make_course(capacity=30, enrolled=30)
        assert registration_decision(s, c) == "WAITLISTED"

    # --- already registered ECP — FR-05 ---
    def test_ecp_not_already_registered(self):
        """ECP/FR-05 | Not in registered_courses -> not ALREADY_REGISTERED"""
        s = make_student(registered=set())
        c = make_course(code="CS201")
        assert registration_decision(s, c) != "ALREADY_REGISTERED"

    def test_ecp_already_registered(self):
        """ECP/FR-05 | In registered_courses -> ALREADY_REGISTERED"""
        s = make_student(registered={"CS201"})
        c = make_course(code="CS201")
        assert registration_decision(s, c) == "ALREADY_REGISTERED"

    # --- course credit_hours ECP — FR-02 ---
    def test_ecp_course_credits_valid(self):
        """ECP/FR-02 | credit_hours in [1,4] -> no ValueError"""
        for hrs in (1, 2, 3, 4):
            assert check_credit_limit(0, hrs) is True

    def test_ecp_course_credits_invalid(self):
        """ECP/FR-02 | credit_hours outside [1,4] -> ValueError"""
        for hrs in (0, 5, -1):
            with pytest.raises(ValueError, match="Invalid course credits"):
                check_credit_limit(0, hrs)


class TestBVA:
    """Boundary values: on-boundary + just-outside."""

    # current_credits boundary [0, 18]
    def test_bva_current_credits_lower_min(self):
        """BVA/FR-02 | current = -1 (just outside) -> ValueError"""
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(-1, 1)

    def test_bva_current_credits_on_min(self):
        """BVA/FR-01 | current = 0 (on min) -> True"""
        assert check_credit_limit(0, 1) is True

    def test_bva_current_credits_on_max(self):
        """BVA/FR-02 | current = 18 (on max, valid) -> False (18+1 >18)"""
        assert check_credit_limit(18, 1) is False

    def test_bva_current_credits_just_above_max(self):
        """BVA/FR-02 | current = 19 (just outside) -> ValueError"""
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(19, 1)

    # new_credits boundary [1, 4]
    def test_bva_new_credits_below_min(self):
        """BVA/FR-02 | new = 0 (just outside) -> ValueError"""
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(10, 0)

    def test_bva_new_credits_on_min(self):
        """BVA/FR-01 | new = 1 (on min) -> True"""
        assert check_credit_limit(10, 1) is True

    def test_bva_new_credits_on_max(self):
        """BVA/FR-01 | new = 4 (on max) -> True (10+4=14)"""
        assert check_credit_limit(10, 4) is True

    def test_bva_new_credits_above_max(self):
        """BVA/FR-02 | new = 5 (just outside) -> ValueError"""
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(10, 5)

    # Combined exactly 18 (allowed per FR-01)
    def test_bva_combined_exactly_18(self):
        """BVA/FR-01 | 15 + 3 = 18 exactly -> True"""
        assert check_credit_limit(15, 3) is True

    def test_bva_combined_just_over_18(self):
        """BVA/FR-01 | 16 + 3 = 19 -> False"""
        assert check_credit_limit(16, 3) is False

    # Availability boundary around capacity
    def test_bva_availability_one_below_capacity(self):
        """BVA/FR-08 | enrolled = capacity-1 -> REGISTERED"""
        s = make_student()
        c = make_course(capacity=30, enrolled=29)
        assert registration_decision(s, c) == "REGISTERED"

    def test_bva_availability_at_capacity(self):
        """BVA/FR-08 | enrolled = capacity -> WAITLISTED"""
        s = make_student()
        c = make_course(capacity=30, enrolled=30)
        assert registration_decision(s, c) == "WAITLISTED"

    def test_bva_capacity_invalid_zero(self):
        """BVA/FR-15 | capacity = 0 -> ValueError"""
        s = make_student()
        c = make_course(capacity=0, enrolled=0)
        with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
            registration_decision(s, c)

    def test_bva_enrolled_negative(self):
        """BVA/FR-15 | enrolled = -1 -> ValueError"""
        s = make_student()
        c = make_course(capacity=30, enrolled=-1)
        with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
            registration_decision(s, c)

    def test_bva_enrolled_exceeds_capacity(self):
        """BVA/FR-15 | enrolled = capacity+1 -> ValueError"""
        s = make_student()
        c = make_course(capacity=30, enrolled=31)
        with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
            registration_decision(s, c)

    # Dues near zero
    def test_bva_dues_exactly_zero(self):
        """BVA/FR-04 | dues = 0 (on boundary) -> REGISTERED"""
        s = make_student(dues=0)
        assert registration_decision(s, make_course()) == "REGISTERED"

    def test_bva_dues_exactly_one(self):
        """BVA/FR-04 | dues = 1 (just outside) -> DUES_BLOCK"""
        s = make_student(dues=1)
        assert registration_decision(s, make_course()) == "DUES_BLOCK"



class TestDecisionTable:

    def test_dt_all_clear_registered(self):
        """DT | D=F,A=F,P=F,C=F,F=F -> REGISTERED"""
        s = make_student()
        c = make_course(capacity=30, enrolled=0)
        assert registration_decision(s, c) == "REGISTERED"

    def test_dt_dues_priority_over_duplicate(self):
        """DT/FR-09 | D=T,A=T -> DUES_BLOCK (D has priority)"""
        s = make_student(dues=500, registered={"CS201"})
        c = make_course(code="CS201")
        assert registration_decision(s, c) == "DUES_BLOCK"

    def test_dt_duplicate_priority_over_prereq(self):
        """DT/FR-09 | D=F,A=T,P=T -> ALREADY_REGISTERED"""
        s = make_student(registered={"CS201"}, completed=set())
        c = make_course(code="CS201", prereqs={"X"})
        assert registration_decision(s, c) == "ALREADY_REGISTERED"

    def test_dt_prereq_priority_over_credit_limit(self):
        """DT/FR-09 | D=F,A=F,P=T,C=T -> PREREQUISITES_MISSING"""
        s = make_student(credits=18, completed=set())
        c = make_course(credits=3, prereqs={"X"})
        assert registration_decision(s, c) == "PREREQUISITES_MISSING"

    def test_dt_credit_limit_priority_over_full(self):
        """DT/FR-09 | D=F,A=F,P=F,C=T,F=T -> CREDIT_LIMIT"""
        s = make_student(credits=18)
        c = make_course(credits=3, capacity=1, enrolled=1)
        assert registration_decision(s, c) == "CREDIT_LIMIT"

    def test_dt_full_only(self):
        """DT | D=F,A=F,P=F,C=F,F=T -> WAITLISTED"""
        s = make_student()
        c = make_course(capacity=1, enrolled=1)
        assert registration_decision(s, c) == "WAITLISTED"

    def test_dt_prereq_missing(self):
        """DT/FR-06 | Prereq not all met -> PREREQUISITES_MISSING"""
        s = make_student(completed={"CS101"})
        c = make_course(prereqs={"CS101", "MATH101"})
        assert registration_decision(s, c) == "PREREQUISITES_MISSING"

    def test_dt_credit_limit_only(self):
        """DT/FR-07 | credits=16, course=3 -> CREDIT_LIMIT"""
        s = make_student(credits=16)
        c = make_course(credits=3)
        assert registration_decision(s, c) == "CREDIT_LIMIT"


class TestStateChanges:

    def test_register_success_updates_state(self):
        """A4/FR-11 | REGISTERED -> credits += hours, enrolled += 1, course in set"""
        s = make_student(credits=0)
        c = make_course(code="CS201", credits=3, capacity=30, enrolled=0)
        assert register_course(s, c) == "REGISTERED"
        assert s.current_credits == 3
        assert "CS201" in s.registered_courses
        assert c.enrolled == 1

    def test_register_dues_block_no_state_change(self):
        """A4/FR-12 | DUES_BLOCK -> state unchanged"""
        s = make_student(dues=1, credits=0)
        c = make_course(capacity=30, enrolled=0)
        assert register_course(s, c) == "DUES_BLOCK"
        assert s.current_credits == 0
        assert s.registered_courses == set()
        assert c.enrolled == 0

    def test_register_waitlisted_no_credit_change(self):
        """A4/FR-12 | WAITLISTED -> waitlist gets id, credits unchanged, enrolled unchanged"""
        s = make_student(sid="S100", credits=0)
        c = make_course(capacity=1, enrolled=1)
        assert register_course(s, c) == "WAITLISTED"
        assert "S100" in c.waitlist
        assert s.current_credits == 0
        assert c.enrolled == 1
        assert "CS201" not in s.registered_courses

    def test_waitlist_no_duplicate_entry(self):
        """A4/FR-12 | Same student waitlisted twice -> list has 1 entry"""
        s = make_student(sid="S100")
        c = make_course(capacity=1, enrolled=1)
        register_course(s, c)
        register_course(s, c)
        assert c.waitlist.count("S100") == 1

    def test_register_credit_limit_no_state_change(self):
        """A4/FR-12 | CREDIT_LIMIT -> no state change"""
        s = make_student(credits=18)
        c = make_course(credits=1, capacity=30, enrolled=0)
        assert register_course(s, c) == "CREDIT_LIMIT"
        assert s.current_credits == 18
        assert s.registered_courses == set()
        assert c.enrolled == 0

    def test_withdraw_enrolled_updates_state(self):
        """A4/FR-13 | Enrolled -> withdraw removes course, subtracts credits,
        decrements enrolled."""
        s = make_student(credits=3, registered={"CS201"})
        c = make_course(code="CS201", credits=3, capacity=30, enrolled=1)
        assert withdraw_course(s, c) is True
        assert s.current_credits == 0
        assert "CS201" not in s.registered_courses
        assert c.enrolled == 0

    def test_withdraw_not_enrolled_returns_false_no_change(self):
        """A4/FR-14 | Not enrolled -> False, no state change"""
        s = make_student(credits=3)
        c = make_course(credits=3, capacity=30, enrolled=1)
        assert withdraw_course(s, c) is False
        assert s.current_credits == 3
        assert c.enrolled == 1

    def test_decision_does_not_mutate_state(self):
        """A4/FR-10 | registration_decision must not mutate either object"""
        s = make_student(credits=0)
        c = make_course(capacity=30, enrolled=0)
        snap_s = (s.current_credits, set(s.registered_courses))
        snap_c = (c.enrolled, list(c.waitlist))
        registration_decision(s, c)
        assert (s.current_credits, set(s.registered_courses)) == snap_s
        assert (c.enrolled, list(c.waitlist)) == snap_c
