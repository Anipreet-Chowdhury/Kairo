from enum import StrEnum


class ProfileRole(StrEnum):
    STUDENT = "student"
    PROFESSOR = "professor"


class CollaborationType(StrEnum):
    INDIVIDUAL = "individual"
    TEAM_BASED = "team_based"


class TermType(StrEnum):
    FALL = "fall"
    WINTER = "winter"
    SUMMER = "summer"


class MembershipStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    REMOVED = "removed"


class AssessmentType(StrEnum):
    EXAM = "exam"
    TEST = "test"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PROGRAMMING_ASSIGNMENT = "programming_assignment"
    LAB = "lab"
    REPORT = "report"
    PROJECT = "project"
    PROJECT_CHECKPOINT = "project_checkpoint"
    PRESENTATION = "presentation"
    DISCUSSION = "discussion"
    OTHER = "other"
