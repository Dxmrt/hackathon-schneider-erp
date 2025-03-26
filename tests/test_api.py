import requests

url = "http://localhost:3000/api"


def test_request_product():
    answ = requests.get(f"{url}/products", params={"part_id": 1})
    assert answ.status_code == 200
    assert answ.json().get("id", None) == 1
    assert answ.json().get("type", None) == "A05"
    assert answ.json().get("stock", None) == 76
    assert answ.json().get("status", None) == "ok"


def test_request_product_2():
    answ = requests.get(f"{url}/products", params={"part_id": 33})
    assert answ.status_code == 500


def test_request_technicians():
    answ = requests.get(f"{url}/technicians/nearest", params={"lat": 54, "lon": 34})
    assert answ.status_code == 200
    techs = answ.json()
    assert len(techs) == 2
    assert techs[0].get("distance_km", None) == 559.86
    assert techs[0].get("id", None) == 4
    assert techs[0].get("name", None) == "Grace"
    assert techs[1].get("distance_km", None) == 641.38
    assert techs[1].get("id", None) == 1
    assert techs[1].get("name", None) == "Ian"


def test_request_technicians_2():
    answ = requests.get(f"{url}/technicians/nearest", params={"sss": 1, "ldat": 4})
    assert answ.status_code == 400
