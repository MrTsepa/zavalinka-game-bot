from enum import Enum, auto


class Message(Enum):
    START = auto()
    ADD_ME_SUCCESS = auto()
    ADD_ME_DUB = auto()
    REMOVE_ME_SUCCESS = auto()
    REMOVE_ME_FAIL = auto()
    UNKNOWN_USER = auto()
    GAME_START_1 = auto()
    GAME_START_2 = auto()
    ROUND_START_1 = auto()
    ROUND_START_2 = auto()
    NO_VERSIONS = auto()
    ANSWER_SAVED = auto()
    VOTE_READY = auto()
    VOTE_SUCCESS = auto()
    ROUND_END_1 = auto()
    ROUND_END_2 = auto()
    QUESTIONS_ENDED = auto()
    PRIVATE_NEED_REPLY = auto()
    GAME_END = auto()
