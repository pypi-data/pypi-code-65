from typing import Dict 
from typing import List
from typing import Union 

StringDict = Dict[str, str]
StringList = List[str]

from .settings import Settings

from .dictionary_setting import DictionarySetting

from .list_setting import ListSetting

from .terminus_setting import TerminusSetting

from .number_setting import NumberSetting

from .stringset_setting import StringSetSetting

from .space import Space

from .error import SettingRangeKeyError
from .error import SettingRangeTypeError
from .error import SettingStringSelectionError
from .error import SettingNotFoundError
from .error import SettingCheckError
from .error import SettingTypeError
from .error import SettingErrorMessage
from .error import OptionsAttributeNotImplementedError
from .error import OptionsAttributeTypeError    
from .error import TypeAttributeNotImplementedError
from .error import TypeAttributeTypeError
from .error import ConsistencyError

