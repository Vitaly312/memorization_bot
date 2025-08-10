class NotFoundException(Exception):
    '''base exception for not found errors'''

class SectionNotFoundException(NotFoundException):
    pass

class QuestionNotFoundException(NotFoundException):
    pass

class UserNotFoundException(NotFoundException):
    pass

class AlreadyExistsException(Exception):
    '''base exception for already exists errors'''

class SectionAlreadyExistsException(AlreadyExistsException):
    pass

class UserAlreadyExistsException(AlreadyExistsException):
    pass