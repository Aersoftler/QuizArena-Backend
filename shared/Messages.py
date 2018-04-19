from enum import Enum


class Messages(Enum):
    # USER
    PW_CHANGED_SUCCESS = 'pw_changed_success'
    DISPLAY_NAME_CHANGED_SUCCESS = 'display_name_changed_success'
    SCORE_ADDED_SUCCESS = 'score_added_success'
    USER_REGISTERED_SUCCESS = 'user_registered_success'
    USER_LOGIN_SUCCESS = 'user_login_success'
    USER_LOGOUT_SUCCESS = 'user_logout_success'
    USER_TOKEN_CORRECT = 'user_token_correct'
    # SESSION
    USER_ADDED_SUCCESS = 'user_added_success'
    SCORE_SET_SUCCESS = 'score_set_success'
    SESSION_CREATED_SUCCESS = 'session_created_success'
    # CATEGORY
    CATEGORY_ADDED_SUCCESS = 'category_added_success'


class Errors(Enum):
    # USER
    NOT_EXISTING_USER = 'not_existing_user'
    NO_DISPLAY_NAME = 'no_display_name'
    NO_PW = 'no_pw'
    OLD_PW_MISMATCH = 'old_pw_missmatch'
    NO_VALID_UPDATE_PARAM = 'no_valid_update_param'
    USER_ALREAFY_EXISTING = 'user_already_existing'
    USER_TOKEN_NOT_CORRECT = 'user_token_not_correct'
    # SESSION
    USER_NOT_FOUND = 'user_not_found'
    NO_MATCHING_CATEGORY = 'no_matching_categroy'
    TYPE_MISMATCH = 'type_missmatch'
    TOO_MANY_QUESTIONS = 'too_many_questions'
    NO_PW_FOR_PRIVATE_SESSION = 'no_pw_for_private_session'
    PERMISSION_DENIED = 'permission_denied'
    # QUESTION
    ANSWER_COUNT_INVALID = 'answer_count_invalid'
    # CATEGORY
    CATEGORY_ALREADY_EXISTS = 'category_exits_already'
    # User and Session
    PW_MISMATCH = 'pw_missmatch'
