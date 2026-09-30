class CourseNotFoundError(Exception):
    pass


class OfferingNotFoundError(Exception):
    pass


class OfferingAlreadyExistsError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


class MembershipAlreadyExistsError(Exception):
    pass


class MembershipNotFoundError(Exception):
    pass


class InvalidMembershipTransitionError(Exception):
    pass
