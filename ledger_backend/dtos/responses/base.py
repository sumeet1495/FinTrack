from typing import List, Dict, Union, Optional
#
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
# DTO class for base response, which includes transaction details, status, message, key, data, and error fields.

@dataclass_json
@dataclass
class BaseResponseDTO:

    transaction_urn: str
    status: str
    response_message: str
    response_key: str
    data:  Optional[Union[List, Dict]] = field(default_factory=dict)
    error: Optional[Union[List, Dict]] = field(default_factory=dict)
