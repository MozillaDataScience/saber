def read_sql_query(path):
    """
	reads in query scaffolding from .sql file specified in <path>
	"""
    with open("./sql/" + path) as f:
        sql_query = f.read()
    return sql_query


def read_json(path):
    """reads in json that lives in <path>"""
    import json

    with open(path) as f:
        json_obj = json.load(f)
    return json_obj


def construct_table_name(spec):
    """generates table name using the author and slug"""
    import re

    # prefix the experiment table with the author's name
    prefix = re.sub(" ", "", spec["author"].lower())
    suffix = re.sub("-", "_", spec["experiment_slug"])

    table_name = "_".join([prefix, suffix])
    return table_name
