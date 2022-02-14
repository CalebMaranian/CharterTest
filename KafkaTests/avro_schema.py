from dataclasses_avroschema import AvroModel, types
from dataclasses import dataclass

@dataclass
class UserModel(AvroModel):
    "An User"
    name: str
    age: int
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"], default="BLUE")
    country: str = "Argentina"
    address: str = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]

