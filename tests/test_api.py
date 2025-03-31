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
    assert techs[0].get("distance_km", None) == 971.48
    assert techs[0].get("id", None) == 8
    assert techs[0].get("name", None) == "Thomas"
    assert techs[1].get("distance_km", None) == 1012.66
    assert techs[1].get("id", None) == 7
    assert techs[1].get("name", None) == "Rachel"


def test_request_technicians_2():
    answ = requests.get(f"{url}/technicians/nearest", params={"sss": 1, "ldat": 4})
    assert answ.status_code == 400
