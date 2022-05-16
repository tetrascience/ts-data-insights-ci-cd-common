context.write_file(file_category="IDS")


def raw_to_ids(input_, context):
    ids = {"foo": "FOO", "bar": "BAR"}
    context.write_file(ids, file_category="IDS")
    # does not raise pylint errors
    causes_pylint_error = "IDS"
    context.write_file(ids, file_category=causes_pylint_error)
    does_not_cause_pylint_error = input_.get("ids_file_category", "IDS")
    context.write_file(ids, file_category=does_not_cause_pylint_error)
