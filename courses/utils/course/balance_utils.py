from courses.models import LessonOccurrence, AttendanceState, LeadFollow, Course
from . import role


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

    absent = [
        attendance.user_id
        for attendance in lesson.attendances.all()
        if attendance.state in AttendanceState.ABSENT_STATES
    ]
    absent_leaders = [u for u in absent if role(u, course) == LeadFollow.LEAD]
    absent_followers = [u for u in absent if role(u, course) == LeadFollow.FOLLOW]
    absent_balance = len(absent_leaders) - len(absent_followers)

    replacements = [
        attendance
        for attendance in lesson.attendances.all()
        if attendance.state in AttendanceState.REPLACEMENT_CONFIRMED
    ]
    replacement_leaders = [a for a in replacements if a.role == LeadFollow.LEAD]
    replacement_followers = [a for a in replacements if a.role == LeadFollow.FOLLOW]
    replacements_balance = len(replacement_leaders) - len(replacement_followers)

    return course_balance - absent_balance + replacements_balance
