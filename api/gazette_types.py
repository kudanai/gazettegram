from enum import Enum
from dataclasses import dataclass


class GazetteType(Enum):
    MASAKKAIY = "masakkaiy"
    GANNAN_BEYNUNVAA = "gannan-beynunvaa"
    KUYYAH_DHINUN = "kuyyah-dhinun"
    KUYYAH_HIFUN = "kuyyah-hifun"
    VAZEEFAA = "vazeefaa"
    THAMREENU = "thamreenu"
    NEELAN = "neelan"
    AANMU_MAULOOMAATHU = "aanmu-mauloomaathu"
    DHENNEVUN = "dhennevun"
    MUBAARAAIY = "mubaaraaiy"
    NOOS_BAYAAN = "noos-bayaan"
    INSURANCE = "insurance"
    BEELAN = "beelan"


@dataclass
class Iulaan:
    id: str
    title: str
    office_name: str
    iulaan_type: str
    additional_info: dict[str, str]
    attachments: dict[str, str]
    body: str
