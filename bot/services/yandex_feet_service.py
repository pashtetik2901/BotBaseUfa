import requests
from bot.config import Config
from typing import Optional, Dict

from bot.helpers.file_logger import CustomLogger


class YandexFeetService:
    def __init__(self, api_url: str, api_key: str, client_id: str, park_id: str):
        self.api_url = api_url
        self.api_key = api_key
        self.client_id = client_id
        self.park_id = park_id
        self.logger = CustomLogger(source="yandex_feet", log_to_file=True, log_to_console=False)

    def get_headers(self):
        return {
            "X-API-Key": self.api_key,
            "X-Client-ID": self.client_id,
            "X-Park-ID": self.park_id,
            "Accept-Language": "ru",
            "Content-Type": "application/json"
        }

    def get_driver_profiles(self, filters: Dict) -> Optional[Dict] | []:
        url = f"{self.api_url}/v1/parks/driver-profiles/list"
        headers = self.get_headers()

        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                    "driver_profile": {
                        "work_status":  [
                            "working"
                        ],
                    },
                }
            },
            "fields": {
                "account": [
                    "id",
                    "type",
                    "balance",
                    "balance_limit",
                ],
                "driver_profile": [
                    "id",
                    'first_name',
                    'last_name',
                    'middle_name',
                    'phones',
                    'work_rule_id',
                    'work_status',
                ]
            },
            "sort_order": [
                {
                    "direction": "asc",
                    "field": "driver_profile.created_date"
                }
            ],
            "limit": filters.get("limit", 100),
            "offset": filters.get("offset", 0)
        }
        # Добавляем секцию driver_profile.work_status, если is_working присутствует в filters
        if filters.get("is_working") is not None:
            payload["query"]["park"]["driver_profile"] = {
                "work_status": ["working"] if filters.get("is_working") else []
            }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("driver_profiles", [])

        self.logger.error(message=f"Ошибка при получении профилей водителей: {response.status_code} - {response.text}")
        return []

    def find_driver_by_phone(self, phone: str, is_working=True):
        limit = 50
        offset = 0

        while True:
            filters = {"limit": limit, "offset": offset, "is_working": is_working}
            driver_profiles = self.get_driver_profiles(filters)

            if not driver_profiles:
                break

            for profile in driver_profiles:
                if phone in profile.get("driver_profile", {}).get("phones", []):
                    self.logger.info(message=f"Найден водитель с телефоном {phone}: {profile}")
                    return profile

            offset += limit

        self.logger.warning(message=f"Водитель с телефоном {phone} не найден")
        return None

    def get_cars(self, filters: Dict) -> Optional[Dict] | []:
        url = f"{self.api_url}/v1/parks/cars/list"
        headers = self.get_headers()

        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                },
            },
            "fields": {
                "car": [
                    "id",
                    "status",
                    "brand",
                    "model",
                    "year",
                    "color",
                    "number",
                    "vin"
                ]
            },
            "limit": filters.get("limit", 100),
            "offset": filters.get("offset", 0)
        }

        if filters.get("id") is not None:
            payload["query"]["park"]["car"] = {
                "id": filters.get("id")
            }

        # Добавляем секцию driver_profile.work_status, если is_working присутствует в filters
        # if filters.get("is_available") is not None:
        #     payload["query"]["park"]["car"] = {
        #         "status": ["unknown", "not_working", "no_driver", "pending", "repairing"] if filters.get("is_available") else []
        #     }

        response = requests.post(url=url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("cars", [])

        return []

    def get_car_by_number(self, number: str, is_available=True):
        limit = 100
        offset = 0

        while True:
            filters = {"limit": limit, "offset": offset, "is_available": is_available}
            cars = self.get_cars(filters)

            if not cars:
                break

            for car in cars:
                if number == car.get("number", None):
                    self.logger.info(message=f"Найден авто с номером {number}: {car}")
                    return car

            offset += limit

        self.logger.warning(message=f"Авто с номером {number} не найден")
        return None

    def get_car_by_id(self, vehicle_id: str):
        url = f"{self.api_url}/v2/parks/vehicles/car"
        headers = self.get_headers()
        params = {"vehicle_id": vehicle_id}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()

        self.logger.error(message=
                         f"Ошибка при получении авто {vehicle_id}: {response.status_code} - {response.text}")
        return None

    def bind_car(self, car_id: str, user_id: str) -> bool:
        url = f"{self.api_url}/v1/parks/driver-profiles/car-bindings"
        headers = self.get_headers()
        params = {
            "car_id": car_id,
            "driver_profile_id": user_id,
            "park_id": self.park_id
        }
        response = requests.put(url=url, headers=headers, params=params)

        if response.status_code in [200, 204]:
            self.logger.info(message=
                             f"За водителем {user_id} закреплен новый авто {car_id}")
            return True

        self.logger.error(message=f"Ошибка при закреплении за водителем {user_id} нового авто {car_id}: {response.status_code} - {response.text}")
        return False

    def get_driver_profile_by_id(self, driver_profile_id: str) -> Optional[Dict]:
        url = f"{self.api_url}/v2/parks/contractors/driver-profile"
        headers = self.get_headers()
        params = {"contractor_profile_id": driver_profile_id}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()

        self.logger.error(message=
                         f"Ошибка при получении профиля водителя {driver_profile_id}: {response.status_code} - {response.text}")
        return None

    def update_driver_profile(self, driver_profile_id: str, data: Dict) -> bool:
        url = f"{self.api_url}/v2/parks/contractors/driver-profile"
        headers = self.get_headers()
        payload = data
        params = {
            "contractor_profile_id": driver_profile_id
        }
        response = requests.put(url=url, headers=headers, params=params, json=payload)
        if response.status_code in [200, 204]:
            self.logger.info(message=
                             f"Обновлен профиль водителя {driver_profile_id}")
            return True

        self.logger.error(message=f"Ошибка при обновлении профиля водителя {driver_profile_id}: {response.status_code} - {response.text}")
        return False


# Инициализация сервиса
yandex_service = YandexFeetService(
    Config.YANDEX_API_URL,
    Config.YANDEX_API_KEY,
    Config.YANDEX_API_CLIENT_ID,
    Config.YANDEX_API_PARK_ID
)