import requests
import pytest
import json

server = "http://127.0.0.1:8002"
game_id = 106
game_id_bad = 0
user_id = 2
user_id_bad = 0


class TestGame():
    def test_game_get_check_status_code_equals_200(self):

        response = requests.get(f"{server}/games/{game_id}")
        assert response.status_code == 200

    def test_game_get_check_status_code_equals_404(self):

        response = requests.get(f"{server}/games/{game_id_bad}")
        assert response.status_code == 404

    def test_game_post_check_status_code_equals_200(self):
        # 
        # new_game = '{"id": 160, "name": "Obelisk Refinement 2021-08-26", "start_date": "2021-08-27 18:24:15.868890", "end_date": null, "is_active": true, "is_voting": false, "owner_id": 2}'
        # response = requests.post(f"{server}/games", headers={"id": 160, "name": "Obelisk Refinement 2021-08-26", "start_date": "2021-08-27 18:24:15.868890", "end_date": null, "is_active": true, "is_voting": false, "owner_id": 2})
        # print(response)
        # assert response.status_code == 200



        # def test_addMessage(self):
        data = {
            "name": "Obelisk Refinement 2021-08-26",
            "is_active": True,
            "is_voting": False,
            "current_user_id": 2
        }
        print(data)
        response = requests.post("/games", json=json.dumps(data))
        print(response)
        json_response = response.json()
        print(json_response)
        assert response.status_code == 200


class TestUser:
    def test_user_get_check_status_code_equals_200(self):
        response = requests.get(f"{server}/users/{user_id}")
        assert response.status_code == 200

    def test_user_get_check_status_code_equals_404(self):
        response = requests.get(f"{server}/users/{user_id_bad}")
        assert response.status_code == 404