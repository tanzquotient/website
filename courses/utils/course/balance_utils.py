from typing import Collection

from courses.models import LessonOccurrence, AttendanceState, LeadFollow, Course


def course_lead_follow_balance(course: Course) -> int:
    """
    balance = #leaders - #followers
    """
    subscriptions = course.subscriptions.all()
    single_leaders = [
        s for s in subscriptions if s.is_single_with_preference(LeadFollow.LEAD)
    ]
    single_followers = [
        s for s in subscriptions if s.is_single_with_preference(LeadFollow.FOLLOW)
    ]
    return len(single_leaders) - len(single_followers)


def lesson_lead_follow_balance(lesson: LessonOccurrence) -> int:
    """
    balance = #leaders - #followers
    """
    course = lesson.course
    course_balance = course_lead_follow_balance(course)
    absent_balance = _balance_for(lesson, AttendanceState.ABSENT_STATES)
    replacements_balance = _balance_for(lesson, [AttendanceState.REPLACEMENT])

    return course_balance - absent_balance + replacements_balance


def _balance_for(lesson: LessonOccurrence, states: Collection[str]) -> int:
    attendances = [
        attendance
        for attendance in lesson.attendances.all()
        if attendance.state in states
    ]
    replacement_leaders = [a for a in attendances if a.role == LeadFollow.LEAD]
    replacement_followers = [a for a in attendances if a.role == LeadFollow.FOLLOW]
    replacements_balance = len(replacement_leaders) - len(replacement_followers)
    return replacements_balance
