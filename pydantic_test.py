from pydantic import BaseModel
from pydantic import ValidationError

class CPE4(BaseModel):
    ipv4_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str

class CPE6(BaseModel):
    ipv6_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str

class Item(BaseModel):
    cm_mac: str
    qos_type: str
    router_ipv6_pd: str
    cpe_ipv4: CPE4
    cpe_ipv6: CPE6

def fill_basemodel():
    cpe4_data = {
        "ipv4_address": "198.51.100.42",
        "port_end": 0,
        "port_start": 0,
        "speedboost_trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "action": "activate"
    }
    cpe4 = CPE4(**cpe4_data)
    cpe6_data = {
        "ipv6_address": "2001:0db8:5b96:0000:0000:426f:8e17:642a",
        "port_end": 0,
        "port_start": 0,
        "speedboost_trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "action": "activate"
    }
    cpe6 = CPE6(**cpe6_data)
    external_data = {
          "cm_mac": "string",
          "qos_type": "speedboost",
          "router_ipv6_pd": "string",
          "cpe_ipv4": cpe4,
          "cpe_ipv6": cpe6
    }
    return Item(**external_data)

if __name__ == "__main__":
    try:
        print(fill_basemodel().json())
    except ValidationError as e:
        print(f"Failure {e.json()}")