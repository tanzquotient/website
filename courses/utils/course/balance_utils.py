from collections.abc import Collection

from courses.models import (
    Attendance,
    AttendanceState,
    Course,
    LeadFollow,
    LessonOccurrence,
    Subscribe,
    SubscribeState,
)


def course_lead_follow_balance(course: Course) -> int:
    """
    balance = #leaders - #followers
    """
    subscriptions = course_accepted_subscriptions(course)
    leaders = [s for s in subscriptions if s.assigned_role() == LeadFollow.LEAD]
    followers = [s for s in subscriptions if s.assigned_role() == LeadFollow.FOLLOW]
    return len(leaders) - len(followers)


def course_accepted_subscriptions(course: Course) -> list[Subscribe]:
    return [
        s
        for s in course.subscriptions.all()
        if s.state in SubscribeState.ACCEPTED_STATES
    ]


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
    attendances = attendances_by_state(lesson, states)
    leaders = [a for a in attendances if a.role == LeadFollow.LEAD]
    followers = [a for a in attendances if a.role == LeadFollow.FOLLOW]
    return len(leaders) - len(followers)


def attendances_by_state(
    lesson: LessonOccurrence,
    states: Collection[str],
) -> list[Attendance]:
    participant_ids = {s.user_id for s in course_accepted_subscriptions(lesson.course)}
    return [
        attendance
        for attendance in lesson.attendances.all()
        if attendance.state in states
        and _matches_participation(attendance, participant_ids)
    ]


def _matches_participation(attendance: Attendance, participant_ids: set[int]) -> bool:
    is_participant = attendance.user_id in participant_ids
    if attendance.state == AttendanceState.REPLACEMENT:
        return not is_participant
    return is_participant
