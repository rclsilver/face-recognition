import json
import pathlib


def load_defaults(filename, **kwargs):
    with (pathlib.Path(__file__).parent / 'defaults' / filename).open('r') as f:
        data = json.load(f)
        data.update(kwargs)
        return data


def create_row(database, model_cls, default_data, custom_data):
    data = {
        **default_data,
        **custom_data,
    }
    result = model_cls()

    for key, value in data.items():
        setattr(result, key, value)

    database.add(result)
    database.commit()

    return result
