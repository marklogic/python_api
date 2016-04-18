#
# Copyright 2015, 2016 MarkLogic Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0#
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# File History
# ------------
#
# Paul Hoehne       03/26/2015     Initial development
#

"""
MarkLogic exception classes.
"""


class MLManageException(Exception):
    """
    Base class for MarkLogic manage exceptions.
    """
    pass


class UnauthorizedAPIRequest(MLManageException):
    """
    This exception class is for exceptions that arise from attempts to
    use endpoints in ways that are unauthorized (HTTP returns 401).

    """
    pass


class UnsupportedOperation(MLManageException):
    """
    This exception class is for exceptions that arise from attempts to
    use the API in ways that are not yet defined.

    """
    pass


class InvalidAPIRequest(MLManageException):
    """
    This exception class is for exceptions that arise when Management API
    responses do not satisfy necessary preconditions, such as attempting
    to read an XDBC server as if it was an HTTP server.

    """
    pass


class UnexpectedManagementAPIResponse(MLManageException):
    """This exception class is for exceptions that arise from unexpected
    management API responses.
    """
    pass


class UnexpectedAPIResponse(MLManageException):
    """This exception class is for exceptions that arise from unexpected
    REST api responses when dealing with search or documents.
    """
    pass
