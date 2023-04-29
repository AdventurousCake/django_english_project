import requests
import re
from multiprocessing import Pool


def send_req(item):
    check = item[4].post('https://hh.ru/applicant/vacancy_response/popup',
                         data={"incomplete": False, "vacancy_id": int(item[0]), "resume_hash": f"{item[1]}",
                               "ignore_postponed": True, "_xsrf": f"{item[2]}", "letter": f"{item[3]}", "lux": True,
                               "withoutTest": "no", "hhtmFromLabel": "undefined", "hhtmSourceLabel": "undefined"})

    print(check.status_code, item[0])
    if check.status_code != 200:
        if check.json()['error'] == 'negotiations-limit-exceeded':
            return False


if __name__ == "__main__":
    n = 0
    req = requests.Session()

    """
    Привет! Чтобы скрипт заработал надо заполнить несколько полей, иначе HH не пустит запросы
    Введи сюда сво куки. Важно быть залогиненым на HH. Проще всего это сделав скопировав все как HAR . Дальше нас инетерсует все что после 'Cookie:' до следующего поля с ':' (это может быть 'X-hhtmFrom:') или что-то другое. Главное забрать все после кук
    """

    # SAVE REQ AS CURL
    # x = """_xsrf=7cd14fa385fee8ad492c229428e18c00; hhuid=1oovfjes3xPwzF\u0021KPtQ\u0021DQ--; __ddg1_=KIfcQl3wGAd0TSljpAWY; region_clarified=NOT_SET; crypted_hhuid=2C45C62FC4F4C8AAF720DC9F202AEF8D122988F92840EB7C526924BE651195E4; iap.uid=ab72ab54234f405586289a7ee5cf24c1; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; redirect_host=surgut.hh.ru; display=desktop; GMT=5; total_searches=24; regions=147; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; hhtoken=AphEiKDxmjBKn1cLhkJrUo1qfoCh; _hi=95187901; hhrole=applicant; device_breakpoint=s; __zzatgib-w-hh=MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXzAwPmlPYEwSJUoQfjYrIBV5a1gLDxNkc0l1dCltaU8YOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEW1V6LB4Xem4mUH8PVy8NPjteLW8PKhMjZHYhP04hC00+KlwVNk0mbjN3RhsJHlksfEspNRMLCVgeQnxuLAg9EWRzSG8vL0MiJmhHXChGDwp+Wh8XfGtVUw89X0EzaWVpcC9gIBIlEU1HGEVkW0I2KBVLcU8cenZffSpBbR5mTF8iRlhNCi4Ve0M8YwxxFU11cjgzGxBhDyMOGFgJDA0yaFF7CT4VHThHKHIzd2UyQGYlZlBZIDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishEn5wKVIKDlw9Q2llbQwtUlFRS2IPHxo0aQteTA==ss+7+w==; __zzatgib-w-hh=MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXzAwPmlPYEwSJUoQfjYrIBV5a1gLDxNkc0l1dCltaU8YOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEW1V6LB4Xem4mUH8PVy8NPjteLW8PKhMjZHYhP04hC00+KlwVNk0mbjN3RhsJHlksfEspNRMLCVgeQnxuLAg9EWRzSG8vL0MiJmhHXChGDwp+Wh8XfGtVUw89X0EzaWVpcC9gIBIlEU1HGEVkW0I2KBVLcU8cenZffSpBbR5mTF8iRlhNCi4Ve0M8YwxxFU11cjgzGxBhDyMOGFgJDA0yaFF7CT4VHThHKHIzd2UyQGYlZlBZIDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishEn5wKVIKDlw9Q2llbQwtUlFRS2IPHxo0aQteTA==ss+7+w==; cfidsgib-w-hh=5DTkmn8mcGKpyj3Gv+96rIFGbXDo26FAf9qys/tKc63gRqyCRx5WWyPylDWJNnH/V8sQptZFjPZwQrn/iWTnBqTYInz3jHlHeVDJ7CI+Gl06CT8CWV2jK259stYTUvPB1QOtys5isnk4kSYYYaZ+VGA0wARJhnoTK+q/4vMr; cfidsgib-w-hh=5DTkmn8mcGKpyj3Gv+96rIFGbXDo26FAf9qys/tKc63gRqyCRx5WWyPylDWJNnH/V8sQptZFjPZwQrn/iWTnBqTYInz3jHlHeVDJ7CI+Gl06CT8CWV2jK259stYTUvPB1QOtys5isnk4kSYYYaZ+VGA0wARJhnoTK+q/4vMr; cfidsgib-w-hh=5DTkmn8mcGKpyj3Gv+96rIFGbXDo26FAf9qys/tKc63gRqyCRx5WWyPylDWJNnH/V8sQptZFjPZwQrn/iWTnBqTYInz3jHlHeVDJ7CI+Gl06CT8CWV2jK259stYTUvPB1QOtys5isnk4kSYYYaZ+VGA0wARJhnoTK+q/4vMr; gsscgib-w-hh=3lh2i+6Pw4xKxBVTdmxkWV6oVLFIUYLuIBgj8rP6cqlwV7PZ3ESV9CDs2+rxD4Ryhm4ZRSePyC8CPJ9C8xF+Qz87d8raSSlDdqBgDaYj4t4C0tif1NTTiFBMkPTnnt3bavM2kO+AX08ALUaD0Ga/3rb7EGNnAOPlf1VzJzYWhmp4iS2bFztrXn04ja0HdX9c4CSIStQsjRsk6nxDxecgph3ses9dEaHC99YiZf+7HAjjvIAaLAvfIoAstJAj8UgY4Cg=; gsscgib-w-hh=3lh2i+6Pw4xKxBVTdmxkWV6oVLFIUYLuIBgj8rP6cqlwV7PZ3ESV9CDs2+rxD4Ryhm4ZRSePyC8CPJ9C8xF+Qz87d8raSSlDdqBgDaYj4t4C0tif1NTTiFBMkPTnnt3bavM2kO+AX08ALUaD0Ga/3rb7EGNnAOPlf1VzJzYWhmp4iS2bFztrXn04ja0HdX9c4CSIStQsjRsk6nxDxecgph3ses9dEaHC99YiZf+7HAjjvIAaLAvfIoAstJAj8UgY4Cg=; fgsscgib-w-hh=cJ8S84e6ea91cce428ac3c5a771d3271a2df57d1; fgsscgib-w-hh=cJ8S84e6ea91cce428ac3c5a771d3271a2df57d1"""
    # x = """hhuid=UiSoIupvLv98CF60QGMqrw--; _xsrf=5d75c4af80803c58fac1df61266dfafa; _xsrf=5d75c4af80803c58fac1df61266dfafa; display=desktop; GMT=5; remember=0; lrp=""; lrr=""; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; total_searches=5; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; __ddg1_=dRYnP4GhcClOwQOR2Iil; iap.uid=4e7efc9f17e44edf89f0466011dd1b91; crypted_hhuid=E2F5AAAA1A010A6EB9623314CBDDFF22AACD72B820E86C8F7DD89F3C9DC97FA8; redirect_host=hh.ru; region_clarified=hh.ru; __zzatundefined=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS93K3tcQB4iYlASVUleCwgnTRd/KCxYfw5kQHMqeF5BayJfeV0ndVlRayELUTQ1ZhBKT01HMzg/aH0eVBw5VREPFhI2FyMSfXIkUAgSXkBBc3MrN1dhMA8WEU1HDTJoUXtMZxUTRkIce3AtLGxzVycyOSdQfyIKay8LGnxsK1YQC1wvPV87Xn0wVioTSyk1IBlAZ0pINF0fQUtEIHIzd3QvQmYeYE5cIkNbTXwhC1VIM1hBEXUmCQs6Lm0tOhlRfRpdehIXQWdST0NdLSJxURR5DiplMy1rIF97FFJ1Vk19WB0RfygjVzs9XUNGK3pabGwjGUsWVTVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeisgEnhsKlIKC2E9R2llbQwtUlFRS2IPHxo0aQteTA==9fzGmw==; __ddgid_=ncomd3L16kgV86MM; regions=1; total_searches=1; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; hhtoken=huE5OotOXa_fJHj3riEir7JNsi\u0021N; hhrole=applicant; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; _hi=95187901; __zzatgib-w-hh=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS93K3tcQB4iYlASVUleCwgnTRd/KCxYfw5kQHMqeF5BayJfeV0ndVlRayELUTQ1ZhBKT01HMzg/aH0eVBw5VREPFhI2FyMSfXMkV38UXD1EcHUpN1dhMA8WEU1HDTJoUXtMZxUTRkIce3AtLGxzVycyOSdQfyIKay8LGnxsK1YQC1wvPV87Xn0wVioTSyk1IBlAZ0pINF0fQUtEIHIzd3QvQ2YlX1BaH0ZYT3shC1VIM1hBEXUmCQs6Lm0tOhlRfRpdehIXQWdST0NdLSJxURR5DiplMy0gIGhIYCVHDgl9JUsYem0rUH8PFz5IdnQvbGceHU1iVDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishEn9rLFB/Dl4/RWllbQwtUlFRS2IPHxo0aQteTA==cMEajA==; gssc58=; cfidsgib-w-hh=sp9nNwJthYoToFvc4uMJFX3WUwdI9x2rwtZuPsvK01iQddBhWSvPLePtL5UHNoxMDTvygtrlYPiVVdd542A9nL4hDGsDTJGznhJN9Kvc7sPwuGmiCNbFAMEqWSI6NitAo+L7oLp1UjRJyLL7sQHlaZ9pWjX5prdHfj6sjlWs; cfidsgib-w-hh=sp9nNwJthYoToFvc4uMJFX3WUwdI9x2rwtZuPsvK01iQddBhWSvPLePtL5UHNoxMDTvygtrlYPiVVdd542A9nL4hDGsDTJGznhJN9Kvc7sPwuGmiCNbFAMEqWSI6NitAo+L7oLp1UjRJyLL7sQHlaZ9pWjX5prdHfj6sjlWs; gsscgib-w-hh=tL4rsbUZhAC1B8Vr/N3+Wq+fUG/sm9zLkRCwfV8MNLDZbaLNkuvjsQdZMm+uYuhHe79rGn0bYiG7XgUmulYUvmIXuvHoKNtyxZ3m3jCFV+cbGIVt6WXjej71kcROEDCiePdGnzQ+fHP3feXi39vzO1vX9cEEL+GCSMovzqlG7L56PU5wsCqxCRgWi8p0tu62QCMe2uCsYPrwPT88aL6pLPzQseMeaDMQUfxreDO+CgL0roHh9SkHenDitkuLp1qpa7g=; device_breakpoint=s; fgsscgib-w-hh=nKuF94ff2ff62527710139b042056019eee7ebb1"""
    # x = """hhuid=UiSoIupvLv98CF60QGMqrw--; _xsrf=5d75c4af80803c58fac1df61266dfafa; _xsrf=5d75c4af80803c58fac1df61266dfafa; display=desktop; GMT=5; remember=0; lrp=""; lrr=""; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; total_searches=5; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; __ddg1_=dRYnP4GhcClOwQOR2Iil; iap.uid=4e7efc9f17e44edf89f0466011dd1b91; crypted_hhuid=E2F5AAAA1A010A6EB9623314CBDDFF22AACD72B820E86C8F7DD89F3C9DC97FA8; redirect_host=hh.ru; region_clarified=hh.ru; __zzatundefined=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS93K3tcQB4iYlASVUleCwgnTRd/KCxYfw5kQHMqeF5BayJfeV0ndVlRayELUTQ1ZhBKT01HMzg/aH0eVBw5VREPFhI2FyMSfXIkUAgSXkBBc3MrN1dhMA8WEU1HDTJoUXtMZxUTRkIce3AtLGxzVycyOSdQfyIKay8LGnxsK1YQC1wvPV87Xn0wVioTSyk1IBlAZ0pINF0fQUtEIHIzd3QvQmYeYE5cIkNbTXwhC1VIM1hBEXUmCQs6Lm0tOhlRfRpdehIXQWdST0NdLSJxURR5DiplMy1rIF97FFJ1Vk19WB0RfygjVzs9XUNGK3pabGwjGUsWVTVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeisgEnhsKlIKC2E9R2llbQwtUlFRS2IPHxo0aQteTA==9fzGmw==; __ddgid_=ncomd3L16kgV86MM; regions=1; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; hhtoken=huE5OotOXa_fJHj3riEir7JNsi\u0021N; hhrole=applicant; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; _hi=95187901; __zzatgib-w-hh=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS93K3tcQB4iYlASVUleCwgnTRd/KCxYfw5kQHMqeF5BayJfeV0ndVlRayELUTQ1ZhBKT01HMzg/aH0eVBw5VREPFhI2FyMSfXMkVw8QZEZFcHotN1dhMA8WEU1HDTJoUXtMZxUTRkIce3AtLGxzVycyOSdQfyIKay8LGnxsK1YQC1wvPV87Xn0wVioTSyk1IBlAZ0pINF0fQUtEIHIzd3QvQ2YlZ0xiKEdYVAghC1VIM1hBEXUmCQs6Lm0tOhlRfRpdehIXQWdST0NdLSJxURR5DiplMy0gIGhIYCVHDgl9JUsYem0rUH8PFz5IdnQvbGceHU1iVDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishEn9zKFgQD15ESmllbQwtUlFRS2IPHxo0aQteTA==dfBdSQ==; cfidsgib-w-hh=wgC/NKDElzIn6hsRuffNvAEirNPugwSN7Ih0RbJN48XDe8g4IXeQ+IpafGgg6CUqeHNcvMVDS9nlVQZrX5lJZ3MItYMHNtz+i9048EgWo3MVfvlI4XniusgzQRgy/yApxE/VhoW694xddo+BFgDiLZGIIQpyKNfOuJgdveMg; cfidsgib-w-hh=wgC/NKDElzIn6hsRuffNvAEirNPugwSN7Ih0RbJN48XDe8g4IXeQ+IpafGgg6CUqeHNcvMVDS9nlVQZrX5lJZ3MItYMHNtz+i9048EgWo3MVfvlI4XniusgzQRgy/yApxE/VhoW694xddo+BFgDiLZGIIQpyKNfOuJgdveMg; gsscgib-w-hh=lQa1GjEBxwv3HR8nY+DTeevFFPdrCGT5R1/J0x0f6j5dZcL02Joomz7a6UnNbxsrsOvY5c2oYuyTCbnTPRu3/vXrvKJSt5FlSg3bGpBsVtlulfFstxfnj+2yKiL1tVyqBVWHqgb712Ucx5zrHy5Wy9k+H/AlsTY/QOCPmSlc55gXBM9JMqbrGhpab1lyZmvhgA1o1CaPPqnA5cW78Brr5hm5pxiVzciy01B/M4aCm3mIsl4iaJmPVpQUe7dGeeCoOQ==; total_searches=5; device_breakpoint=s; fgsscgib-w-hh=ocO698a2ef14d1087f72cebe6df8a253b585295d"""
    x = """hhuid=UiSoIupvLv98CF60QGMqrw--; _xsrf=5d75c4af80803c58fac1df61266dfafa; _xsrf=5d75c4af80803c58fac1df61266dfafa; display=desktop; GMT=5; remember=0; lrp=""; lrr=""; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; total_searches=5; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; __ddg1_=dRYnP4GhcClOwQOR2Iil; iap.uid=4e7efc9f17e44edf89f0466011dd1b91; crypted_hhuid=E2F5AAAA1A010A6EB9623314CBDDFF22AACD72B820E86C8F7DD89F3C9DC97FA8; redirect_host=hh.ru; region_clarified=hh.ru; __zzatundefined=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS93K3tcQB4iYlASVUleCwgnTRd/KCxYfw5kQHMqeF5BayJfeV0ndVlRayELUTQ1ZhBKT01HMzg/aH0eVBw5VREPFhI2FyMSfXIkUAgSXkBBc3MrN1dhMA8WEU1HDTJoUXtMZxUTRkIce3AtLGxzVycyOSdQfyIKay8LGnxsK1YQC1wvPV87Xn0wVioTSyk1IBlAZ0pINF0fQUtEIHIzd3QvQmYeYE5cIkNbTXwhC1VIM1hBEXUmCQs6Lm0tOhlRfRpdehIXQWdST0NdLSJxURR5DiplMy1rIF97FFJ1Vk19WB0RfygjVzs9XUNGK3pabGwjGUsWVTVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeisgEnhsKlIKC2E9R2llbQwtUlFRS2IPHxo0aQteTA==9fzGmw==; __ddgid_=ncomd3L16kgV86MM; regions=1; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; total_searches=1; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; hhtoken=cQUXi4RkrW7ojarzFYlCW_HwonMO; _hi=95187901; hhrole=applicant; device_magritte_breakpoint=s; device_breakpoint=s; gsscgib-w-hh=u4JYNLbGUMw6b0MVrnqMgzk1B38PARdo7fphMF+BEQDHM3qk1zgh5t4AH5IuRJZa4Sbih8glaplFt8XeYbG/fPCZpt33Gsp9/dfDQSfFaVdYOOyorPb9mXml8mUVCTkRssE8EYvpInQuwY5ft6vtCxoLlKsvJIDFCNmmvZ23rBGwv4C6HOhy61S22ydDn3/dM+0p41HV7R7l/BxPKJcwNC6lqUHdCGP37+4LUi4U+rvkZ5RVu9jPwfX4BkbRANuJSbQ=; gssc58=; __zzatgib-w-hh=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS93K3tcQB4iYlASVUleCwgnTRd/KCxYfw5kQHMqeF5BayJfeV0ndVlRayELUTQ1ZhBKT01HMzg/aH0eVBw5VREPFhI2FyMSfXMlVgwRX0NJbXQqN1dhMA8WEU1HDTJoUXtMZxUTRkIce3AtLGxzVycyOSdQfyIKay8LGnxsK1YQC1wvPV87Xn0wVioTSyk1IBlAZ0pINF0fQUtEIHIzd3QvQ2ckZE1dJUtVTn8hC1VIM1hBEXUmCQs6Lm0tOhlRfRpdehIXQWdST0NdLSJxURR5DiplMy1nTmhJYiZ5Vwp6KUwSM3MkCwwPX3J3KC8vPSMfGUgWJzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishE35wKVMNE1s+SmllbQwtUlFRS2IPHxo0aQteTA==utPD5g==; cfidsgib-w-hh=dehhX11UINQluowBdaGvHD0s4juldph2mXFD6A3mtGt2nCbaG2EULByGjBtxsYPZfzlGoFa4ymUvMT8WRKH2qoGtWl7+WZRANd23KdOJt55eYONlwyfqIAQEMjf9aKMNLhRkxOd0P+0iOyAJLXVQQmQ02KE5DuL7tL5gu7um; cfidsgib-w-hh=dehhX11UINQluowBdaGvHD0s4juldph2mXFD6A3mtGt2nCbaG2EULByGjBtxsYPZfzlGoFa4ymUvMT8WRKH2qoGtWl7+WZRANd23KdOJt55eYONlwyfqIAQEMjf9aKMNLhRkxOd0P+0iOyAJLXVQQmQ02KE5DuL7tL5gu7um; fgsscgib-w-hh=QZZeaba7c1eeb5812b90fa32ba607f99bf8da356"""
    cookies = x

    if cookies == "Вставь сюда свои куки":
        raise Exception("Ты забыл вставить сюда свои куки")

    req.headers = {"Host": "hh.ru",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
                   "Cookie": f"""{cookies}"""}

    """Здесь нам нужно вставить хеш резюме. Оно находиться в разделе https://hh.ru/applicant/resumes . Дальше ты должен перейти в одно из своих резюме и скопировать хеш после ссылки . Как пример https://hh.ru/resume/71010d6fff099f0ef20039ed1f497978653133 . Тут нам нужно забрать 71010d6fff099f0ef20039ed1f497978653133 и вставить в поле ниже"""

    # !!! my
    resume_hash = "3d223c3fff0b88a62b0039ed1f387856794335"

    xsrf_token = re.search("_xsrf=(.*?);", cookies).group(1)

    """Ниже вставляем свое письмо. Советую сделать его максимально обобщенным. Больше об этом в мое треде https://twitter.com/ns0000000001/status/1612456900993650688?s=52&t=X3kUKCZQjFDJbTbg9aQWbw """

    # TODO LETTER; upd from keep
    letter = """Здравствуйте, меня заинтересовала вакансия Python разработчика в вашу компанию.
Благодаря своему опыту в python бэкэнд разработке и знанию Python я смогу внести ценный вклад в вашу команду.
Как Python разработчик я отвечал за код, API, интеграцией сервисов, проектированием и работой с БД. 
Мои основные технические навыки: хороший уровень Python 3, Django, Django DRF, PostgreSQL, sqlalchemy.

Также я быстро обучаюсь, хорошо мотивирован и постоянно слежу за трендами IT, онлайн конференциями, чтобы улучшать свои навыки. 
Давайте сотрудничать. 
tg: https://t.me/igor_py9
"""

    if letter == "Вставь сюда свое письмо":
        raise Exception("Ты забыл вставить сюда своё письмо")

    """Дальще переходи на страницу HH и в поиске вбиваем то, что вам интересно. После нажимает Enter и копируем ссыку на которую вас перебросило. Пример который получается при вводе 'автоматизация python': https://hh.ru/search/vacancy?text=автоматизация+python&salary=&schedule=remote&ored_clusters=true&enable_snippets=true"""

    # todo LINK
    # https://surgut.hh.ru/search/vacancy?text=Data+scientist
    py_dev_and_middle = """https://hh.ru/search/vacancy?excluded_text=fullstack%2C+data%2C+ml%2C+senior%2C+%D0%BD%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BD%D0%B8%D0%BA%2C+%D0%BA%D1%83%D1%80%D1%81%D1%8B%2C+%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%2C+%D0%90%D0%B2%D1%82%D0%BE%D1%80+%D1%80%D0%B0%D0%B1%D0%BE%D1%82%2C+devops%2C+Full-stack%2C+c%2B%2B%2C+c%23&professional_role=96&search_field=name&enable_snippets=false&text=Python+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA&from=suggest_post&ored_clusters=true"""
    py_middle_nouniv = """https://surgut.hh.ru/search/vacancy?excluded_text=fullstack%2C+data%2C+ml%2C+senior%2C+%D0%BD%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BD%D0%B8%D0%BA%2C+%D0%BA%D1%83%D1%80%D1%81%D1%8B%2C+%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%2C+%D0%90%D0%B2%D1%82%D0%BE%D1%80+%D1%80%D0%B0%D0%B1%D0%BE%D1%82%2C+devops%2C+Full-stack%2C+c%2B%2B%2C+c%23&education=not_required_or_not_specified&professional_role=96&search_field=name&enable_snippets=false&text=Python+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA&from=suggest_post&ored_clusters=true"""
    
    # done all
    py_dev_nomiddle_nouniv = """https://hh.ru/search/vacancy?excluded_text=middle%2Cmiddle%2B%2Cfullstack%2C+data%2C+ml%2C+senior%2C+%D0%BD%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BD%D0%B8%D0%BA%2C+%D0%BA%D1%83%D1%80%D1%81%D1%8B%2C+%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%2C+%D0%90%D0%B2%D1%82%D0%BE%D1%80+%D1%80%D0%B0%D0%B1%D0%BE%D1%82%2C+devops%2C+Full-stack%2C+c%2B%2B%2C+c%23&education=not_required_or_not_specified&professional_role=96&search_field=name&enable_snippets=false&text=Python+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA&from=suggest_post&ored_clusters=true"""
    dj = """https://hh.ru/search/vacancy?text=django+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA&salary=&professional_role=96&ored_clusters=true&search_field=name&excluded_text=fullstack%2C+data%2C+ml%2C+senior%2C+%D0%BD%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BD%D0%B8%D0%BA%2C+%D0%BA%D1%83%D1%80%D1%81%D1%8B%2C+%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%2C+%D0%90%D0%B2%D1%82%D0%BE%D1%80+%D1%80%D0%B0%D0%B1%D0%BE%D1%82%2C+devops%2C+Full-stack%2C+c%2B%2B%2C+c%23"""

    search_link = py_dev_and_middle
    # search_link = py_dev_nomiddle_nouniv

    if search_link == "Вставь сюда свой поисковый запрос":
        raise Exception("Ты забыл вставить сюда свой запрос")

    pool = Pool(processes=70)

    """Важно, что HH позволяет в день откликаться только на 200 вакансий. Поэтому, как только скрипт получит ошибку о привышения лимита, он автоматически отключиться. Если ты все сделал правильно, то ты будешь видеть в консоли такие записи
    400 76870753
    200 76613497
    400 и 200 статусы это ок. Если ты видишь только 403 или 404 проверь, правильно ли ты вставил куки
    """

    while True:
        data = req.get(f"{search_link}&page={n}").text
        links = re.findall('https://hh.ru/vacancy/(\d*)?', data, re.DOTALL)
        send_dict = []
        for link in links:
            send_dict.append((link, resume_hash, xsrf_token, letter, req))
        if links == []:
            break
        check = pool.map(send_req, send_dict)
        if False in check:
            break
        n += 1
    pool.close()
    pool.join()
