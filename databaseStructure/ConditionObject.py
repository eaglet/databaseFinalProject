from GeneralFunction import GeneralFunction
import operator


# Condition object
class ConditionObject:
    def __init__(self, equal_dict, less_dict, greater_dict, not_equal_dict, greater_equal_dict, less_equal_dict):
        self.equal_dict = equal_dict
        self.less_dict = less_dict
        self.greater_dict = greater_dict
        self.not_equal_dict = not_equal_dict
        self.greater_equal_dict = greater_equal_dict
        self.less_equal_dict = less_equal_dict

    def is_empty(self):
        equal_len = len(self.equal_dict)
        less_len = len(self.less_dict)
        greater_len = len(self.greater_dict)
        not_equal_len = len(self.not_equal_dict)
        greater_equal_len = len(self.greater_equal_dict)
        less_equal_len = len(self.less_equal_dict)

        return equal_len + less_len + greater_len + not_equal_len + greater_equal_len + less_equal_len == 0

    # Transform condition string to array ConditionObject.
    # 'And' condition will be put into a single object and 'Or' condition will be put into separate object
    # type variables: str - user input conditions
    # rtype result: array of ConditionObject
    @staticmethod
    def transform_condition_to_object(variables):
        variables = variables.lower().replace('(', '').replace(')', '')
        result = []
        conditions = []
        variables_or = variables.split('or')

        for variable in variables_or:
            variables_and = variable.split('and')
            conditions.append(variables_and)
        for cond in conditions:
            equal_dict = {}
            less_dict = {}
            greater_dict = {}
            not_equal_dict = {}
            greater_equal_dict = {}
            less_equal_dict = {}
            for item in cond:
                if '=' in item and '>' not in item and '<' not in item and '!' not in item:
                    append_to_dict(equal_dict, '=', item)
                elif '>=' in item:
                    append_to_dict(greater_equal_dict, '>=', item)
                elif '<=' in item:
                    append_to_dict(less_equal_dict, '<=', item)
                elif '>' in item:
                    append_to_dict(greater_dict, '>', item)
                elif '<' in item:
                    append_to_dict(less_dict, '<', item)
                elif '!=' in item:
                    append_to_dict(not_equal_dict, '!=', item)

            result.append(
                ConditionObject(equal_dict, less_dict, greater_dict,
                                not_equal_dict, greater_equal_dict, less_equal_dict))
        return result

    # Check if the db object fulfill the condition object.
    # type cond: ConditionObject
    # type db_object: DbObject
    # type metadata: array
    # rtype boolean
    @staticmethod
    def check_condition(cond, db_object, metadata):

        if not apply_condition(cond.equal_dict, '!=', metadata, db_object):
            return False
        if not apply_condition(cond.less_dict, '>=', metadata, db_object):
            return False
        if not apply_condition(cond.greater_dict, '<=', metadata, db_object):
            return False
        if not apply_condition(cond.not_equal_dict, '==', metadata, db_object):
            return False
        if not apply_condition(cond.greater_equal_dict, '<', metadata, db_object):
            return False
        if not apply_condition(cond.less_equal_dict, '>', metadata, db_object):
            return False

        return True

    # Check if the the value from two tables fulfilled the condition object.
    # type cond: ConditionObject
    # type current_name: str
    # type current_main: DbObject
    # type metadata: array
    # type source_name: str
    # type source_main: DbObject
    # type source_metadata: array
    # rtype boolean
    @staticmethod
    def check_join_condition(cond, current_name, current_main, current_metadata, source_name,
                             source_main, source_metadata):

        if cond.equal_dict and not apply_join_condition(cond.equal_dict, '!=', current_name, current_main, current_metadata, source_main, source_metadata):
            return False
        if cond.less_dict and not apply_join_condition(cond.less_dict, '>=', current_name, current_main, current_metadata, source_main, source_metadata):
            return False
        if cond.greater_dict and not apply_join_condition(cond.greater_dict, '<=', current_name, current_main, current_metadata, source_main, source_metadata):
            return False
        if cond.not_equal_dict and not apply_join_condition(cond.not_equal_dict, '==', current_name, current_main, current_metadata, source_main, source_metadata):
            return False
        if cond.greater_equal_dict and not apply_join_condition(cond.greater_equal_dict, '<', current_name, current_main, current_metadata, source_main, source_metadata):
            return False
        if cond.less_equal_dict and not apply_join_condition(cond.less_equal_dict, '>', current_name, current_main, current_metadata, source_main, source_metadata):
            return False

        return True


ops = {'==': operator.eq, '>=': operator.ge, '<=': operator.le, '!=': operator.ne, '>': operator.gt, '<': operator.lt}


# Check if the db object fulfill the single condition dictionary.
# type condition_dict: ConditionObject
# type op: str
# type metadata: array
# type db_object: DbObject
# rtype boolean
def apply_condition(condition_dict, op, metadata, db_object):

    op_func = ops[op]
    for key in condition_dict:
        index = metadata.index(key)
        for value in condition_dict[key]:
            if op_func(db_object.value[index], value):
                return False

    return True


# Check if the value from two table fulfilled the condition.
# type condition_dict: ConditionObject
# type current_name: str
# type current_main: DbObject
# type current_metadata: array
# type source_main: DbObject
# type source_metadata: array
# rtype boolean
def apply_join_condition(condition_dict, op, current_name, current_main, current_metadata,
                         source_main, source_metadata):

    op_func = ops[op]
    for key in condition_dict:
        parameter1 = key.split('.')
        table1_name = parameter1[0]
        table1_column = parameter1[1]
        for value in condition_dict[key]:
            parameter2 = value.split('.')
            table2_column = parameter2[1]
            if table1_name == current_name:
                table1_require_index = GeneralFunction.get_index_of_metadata(current_metadata, [table1_column])
                table2_require_index = GeneralFunction.get_index_of_metadata(source_metadata, [table2_column])
            else:
                table1_require_index = GeneralFunction.get_index_of_metadata(source_metadata, [table2_column])
                table2_require_index = GeneralFunction.get_index_of_metadata(current_metadata, [table1_column])

            if op_func(current_main.value[table1_require_index[0]], source_main.value[table2_require_index[0]]):
                return False

    return True


# Append the value to target dictionary.
# type target_dict: dictionary
# type op: str
# type item: str - user input condition
def append_to_dict(target_dict, op, item):
    values = item.split(op)
    if target_dict.get(values[0]):
        target_dict[values[0]] = target_dict[values].append(values[0])
    else:
        target_dict[values[0]] = [values[1]]
