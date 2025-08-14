from locust import HttpUser, between, task
import random
import os

os.environ["UNPLUG_TG_ANSWERS"] = "1"

START_CMD = lambda uid: { # noqa: E731
    "message": {
        "chat": {
            "first_name": "TEST",
            "id": uid,
            "type": "private",
            "username": "test_user",
        },
        "date": 1755164262,
        "entities": [{"length": 6, "offset": 0, "type": "bot_command"}],
        "from": {
            "first_name": "TEST",
            "id": uid,
            "is_bot": False,
            "language_code": "ru",
            "username": "test_user",
        },
        "message_id": 1829,
        "text": "/start",
    },
    "update_id": 108080112,
}

START_SURVEY = lambda uid: { # noqa: E731
    "message": {
        "chat": {
            "first_name": "TEST",
            "id": uid,
            "type": "private",
            "username": "test_user",
        },
        "date": 1755164404,
        "entities": [{"length": 13, "offset": 0, "type": "bot_command"}],
        "from": {
            "first_name": "Виталий",
            "id": uid,
            "is_bot": False,
            "language_code": "ru",
            "username": "test_user",
        },
        "message_id": 1831,
        "text": "/start_survey",
    },
    "update_id": 108080113,
}

SELECT_SECTION_1 = lambda uid: { # noqa: E731
    "callback_query": {
        "chat_instance": "5610214012630681107",
        "data": "select_section_:1",
        "from": {
            "first_name": "TEST",
            "id": uid,
            "is_bot": False,
            "language_code": "ru",
            "username": "test_user",
        },
        "id": "6976044302504883464",
        "message": {
            "chat": {
                "first_name": "TEST",
                "id": uid,
                "type": "private",
                "username": "test_user",
            },
            "date": 1755164405,
            "from": {
                "first_name": "TEST",
                "id": 7455518669,
                "is_bot": True,
                "username": "test_bot",
            },
            "message_id": 1832,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"callback_data": "select_section_:1", "text": "1"},
                        {"callback_data": "select_section_:2", "text": "2"},
                    ]
                ]
            },
            "text": "Выберите раздел",
        },
    },
    "update_id": 108080114,
}

SEND_TRUE_ANS = lambda uid: { # noqa: E731
    "message": {
        "chat": {
            "first_name": "TEST",
            "id": uid,
            "type": "private",
            "username": "test_user",
        },
        "date": 1755164411,
        "from": {
            "first_name": "Виталий",
            "id": uid,
            "is_bot": False,
            "language_code": "ru",
            "username": "vitaly_02",
        },
        "message_id": 1835,
        "text": ".",
    },
    "update_id": 108080115,
}

SEND_WROND_ANS = lambda uid: { # noqa: E731
    "message": {
        "chat": {
            "first_name": "Виталий",
            "id": uid,
            "type": "private",
            "username": "vitaly_02",
        },
        "date": 1755164411,
        "from": {
            "first_name": "Виталий",
            "id": uid,
            "is_bot": False,
            "language_code": "ru",
            "username": "vitaly_02",
        },
        "message_id": 1835,
        "text": "FALSE",
    },
    "update_id": 108080115,
}

GET_STAT_CMD = lambda uid: { # noqa: E731
    "message": {
        "chat": {
            "first_name": "TEST",
            "id": uid,
            "type": "private",
            "username": "test_user",
        },
        "date": 1755164597,
        "entities": [{"length": 5, "offset": 0, "type": "bot_command"}],
        "from": {
            "first_name": "TEST",
            "id": 1234567890,
            "is_bot": False,
            "language_code": "ru",
            "username": "test_user",
        },
        "message_id": 1839,
        "text": "/info",
    },
    "update_id": 108080117,
}


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self):
        self.uid = random.randint(1000000000, 9999999999)
        self.client.post("/webhook", json=START_CMD(self.uid))

    @task(1)
    def survey_true_ans(self):
        self.client.post("/webhook", json=START_SURVEY(self.uid))
        self.client.post("/webhook", json=SELECT_SECTION_1(self.uid))
        self.client.post("/webhook", json=SEND_TRUE_ANS(self.uid))

    @task(1)
    def survey_wrong_ans(self):
        self.client.post("/webhook", json=START_SURVEY(self.uid))
        self.client.post("/webhook", json=SELECT_SECTION_1(self.uid))
        self.client.post("/webhook", json=SEND_WROND_ANS(self.uid))

    @task(3)
    def get_stat(self):
        self.client.post("/webhook", json=GET_STAT_CMD(self.uid))
