from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.models import *
from courses.services.courses import get_copy_notes, get_next_level_type


def _type_label(course_type: CourseType) -> str:
    if course_type.level is None:
        return str(course_type)
    return f"{course_type} (level {course_type.level})"


class CopyCourseForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    offering = forms.ModelChoiceField(
        queryset=Offering.objects.all(), label=_("Offering to copy into")
    )

    def __init__(self, *args, courses, advance_levels, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.courses = list(courses)
        self.types = {}
        self.rows = []
        for course in self.courses:
            # successors are the course types set for early sign-up
            types = [course.type, *course.type.successors.all()]
            self.types.update((t.pk, t) for t in types)

            notes = get_copy_notes(course)
            next_type = None
            if advance_levels and not course.cancelled:
                next_type = get_next_level_type(course.type)
                if next_type is None and course.type.level is not None:
                    notes.append(
                        "No unique successor one level higher, check the course type"
                    )

            self.fields[f"copy_{course.pk}"] = forms.BooleanField(
                required=False, initial=True
            )
            self.fields[f"type_{course.pk}"] = forms.TypedChoiceField(
                coerce=int,
                choices=list({t.pk: _type_label(t) for t in types}.items()),
                initial=(next_type or course.type).pk,
            )
            self.rows.append(
                {
                    "course": course,
                    "copy": self[f"copy_{course.pk}"],
                    "type": self[f"type_{course.pk}"],
                    "notes": notes,
                }
            )

    def clean(self):
        cleaned_data = super().clean()
        if not any(cleaned_data.get(f"copy_{c.pk}") for c in self.courses):
            raise ValidationError(_("Select at least one course to copy."))
        return cleaned_data

    def get_courses_to_copy(self) -> list[tuple[Course, CourseType]]:
        return [
            (course, self.types[self.cleaned_data[f"type_{course.pk}"]])
            for course in self.courses
            if self.cleaned_data[f"copy_{course.pk}"]
        ]
