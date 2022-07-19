"""
These imports should each trigger a pylint error
"""
import task_script_utils.convert_datetime_to_ts_format
from task_script_utils.convert_datetime_to_ts_format import convert_datetime_to_ts_format
from task_script_utils.convert_datetime_to_ts_format import convert_datetime_to_ts_format as p_0


"""
These imports should not trigger a pylint error
"""
import task_script_utils.datetime_parser as dtp_0
import task_script_utils.datetime_parser.utils.parsing as dtp_1
from task_script_utils.datetime_parser.utils import parsing as dtp_2

# args don't matter
args = ("2020-01-01", ())
"""
These calls should trigger a pylint error
"""
convert_datetime_to_ts_format(*args)
p_0(*args)

dtp_0.parse(*args)
dtp_0.parser.parse(*args)
dtp_1.parse(*args)
