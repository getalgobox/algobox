import collections

from flask import abort
from flask import make_response
from flask import jsonify


class GetOrThrowDict(collections.UserDict):
    """
    Used to wrap dictionaries which should always have keys we request with
    __getitem__.

    If a key is not present the user has made a mistake, and should
    be informed that they are missing a required key.

    If a key is optional, the get method should be used as this is unchanged.
    """

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError as e:
            abort(make_response(jsonify({
                "error": "the '{}' key is required but was was not found in\
                the object you provided.".format(key).replace("\n", "")
            }), 400))
