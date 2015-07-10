# -*- coding: utf-8 -*-
#
# Copyright 2015 MarkLogic Corporation
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
# Norman Walsh      05/07/2015     Initial development

"""
Classes for dealing with server request blackouts
"""

from marklogic.models.utilities.validators import assert_list_of_type
from marklogic.models.utilities.utilities import PropertyLists

class RequestBlackout(PropertyLists):
    """
    A request blackout period. This is an abstract class.
    """
    def __init__(self):
        raise ValueError("Do not instantiate RequestBlackout directly")

    def blackout_type(self):
        """
        The blackout type.
        """
        return self._config['blackout_type']

    def user_names(self):
        """
        The names of the users to whom this blackout applies.
        """
        if 'user' in self._config:
            return self._config['user']
        return None

    def add_user_name(self, user):
        """
        Add a user name to the list of blackout names.
        """
        return self.add_to_property_list('user', user)

    def set_user_names(self, users):
        """
        Set the user names to the list of blackout names.
        """
        return self.set_property_list('user', users)

    def remove_user_name(self, user):
        """
        Remove a user names from the list of blackout names.
        """
        return self.remove_from_property_list('user', user)

    def role_names(self):
        """
        The names of the roles to which this blackout applies.
        """
        if 'role' in self._config:
            return self._config['role']
        return None

    def add_role_name(self, role):
        """
        Add a role to the list of blackout roles.
        """
        return self.add_to_property_list('role', role)

    def set_role_names(self, roles):
        """
        Set the list of blackout roles.
        """
        return self.set_property_list('role', roles)

    def remove_role_name(self, role):
        """
        Remove a role from the list of blackout roles.
        """
        return self.remove_from_property_list('role', role)

    @classmethod
    def recurringDuration(cls, days, start_time, duration,
                          users=None, roles=None):
        """
        Create a recurring request blackout period with a duration
        """
        # FIXME: validate args
        return RequestBlackoutRecurringDuration(days, start_time, duration,
                                                users, roles)

    @classmethod
    def recurringStartEnd(cls, days, start_time, end_time,
                          users=None, roles=None):
        """
        Create a recurring request blackout period with start and end times.
        """
        # FIXME: validate args
        return RequestBlackoutRecurringStartEnd(days, start_time, end_time,
                                                users, roles)

    @classmethod
    def recurringAllDay(cls, days, users=None, roles=None):
        """
        Create a recurring request blackout period that lasts all day.
        """
        # FIXME: validate args
        return RequestBlackoutRecurringAllDay(days, users, roles)

    @classmethod
    def oneTimeDuration(cls, start_date, start_time, duration,
                        users=None, roles=None):
        """
        Create a one time request blackout period with a duration.
        """
        # FIXME: validate args
        return RequestBlackoutOneTimeDuration(start_date, start_time, duration,
                                              users, roles)

    @classmethod
    def oneTimeStartEnd(cls, start_date, start_time, end_date, end_time,
                        users=None, roles=None):
        """
        Create a one time request blackout period with a start and end time.
        """
        # FIXME: validate args
        return RequestBlackoutOneTimeStartEnd(start_date, start_time,
                                              end_date, end_time,
                                              users, roles)

class RequestBlackoutRecurringDuration(RequestBlackout):
    """
    A recurring request blackout period for a duration
    """
    def __init__(self, days, start_time, duration,
                 users=None, roles=None):
        """
        Create a recurring request blackout period for a duration
        """
        if users is None and roles is None:
            raise ValidationError('A request blackout must specify users or roles',
                                  None)

        self._config = {
            'blackout-type': 'recurring',
            'day': assert_list_of_type(days, str),
            'period': {
                'start-time': start_time,
                'duration': duration
                }
            }
        if users is not None:
            self._config['user'] = users
        if roles is not None:
            self._config['roles'] = roles

    def days():
        """
        The blackout days.
        """
        return self._config['days']

    def start_time():
        """
        The blackout start time.
        """
        return self._config['period']['start-time']

    def duration():
        """
        The blackout duration.
        """
        return self._config['period']['duration']

class RequestBlackoutRecurringStartEnd(RequestBlackout):
    """
    A recurring request blackout period with start and end times
    """
    def __init__(self, days, start_time, end_time,
                 users=None, roles=None):
        """
        Create a recurring request blackout period with start and end times
        """
        if users is None and roles is None:
            raise ValidationError('A request blackout must specify users or roles',
                                  None)

        self._config = {
            'blackout-type': "recurring",
            'day': assert_list_of_type(days, str),
            'period': {
                'start-time': start_time,
                'end-time': end_time
                }
            }
        if users is not None:
            self._config['user'] = users
        if roles is not None:
            self._config['roles'] = roles

    def days():
        """
        The blackout days.
        """
        return self._config['days']

    def start_time():
        """
        The blackout start time.
        """
        return self._config['period']['start-time']

    def end_time():
        """
        The blackout end time.
        """
        return self._config['period']['end-time']

class RequestBlackoutRecurringAllDay(RequestBlackout):
    """
    A recurring request blackout period for a whole day
    """
    def __init__(self, days, users=None, roles=None):
        """
        Create a recurring request blackout period for a whole day
        """
        if users is None and roles is None:
            raise ValidationError('A request blackout must specify users or roles',
                                  None)

        self._config = {
            'blackout-type': "recurring",
            'day': assert_list_of_type(days, str),
            'period': None
            }
        if users is not None:
            self._config['user'] = users
        if roles is not None:
            self._config['roles'] = roles

    def days():
        """
        The blackout days.
        """
        return self._config['days']

class RequestBlackoutOneTimeDuration(RequestBlackout):
    """
    A one time request blackout period with a duration
    """
    def __init__(self, start_date, start_time, duration,
                 users=None, roles=None):
        """
        Create a one time request blackout period with a duration
        """

        if users is None and roles is None:
            raise ValidationError('A request blackout must specify users or roles',
                                  None)

        self._config = {
            'blackout-type': "once",
            'period': {
                'start-date': start_date,
                'start-time': start_time,
                'duration': duration
                }
            }
        if users is not None:
            self._config['user'] = users
        if roles is not None:
            self._config['roles'] = roles

    def start_date():
        """
        The blackout start date.
        """
        return self._config['period']['start-date']

    def start_time():
        """
        The blackout start time.
        """
        return self._config['period']['start-time']

    def duration():
        """
        The blackout duration.
        """
        return self._config['period']['duration']


class RequestBlackoutOneTimeStartEnd(RequestBlackout):
    """
    A one time request blackout period with start and end times
    """
    def __init__(self, start_date, start_time, end_date, end_time,
                 users=None, roles=None):
        """
        Create a one time request blackout period with start and end times
        """

        if users is None and roles is None:
            raise ValidationError('A request blackout must specify users or roles',
                                  None)

        self._config = {
            'blackout-type': "once",
            'period': {
                'start-date': start_date,
                'start-time': start_time,
                'end-date': end_date,
                'end-time': end_time,
                }
            }
        if users is not None:
            self._config['user'] = users
        if roles is not None:
            self._config['roles'] = roles

    def start_date():
        """
        The blackout start date.
        """
        return self._config['period']['start-date']

    def start_time():
        """
        The blackout start time.
        """
        return self._config['period']['start-time']

    def end_date():
        """
        The blackout end date.
        """
        return self._config['period']['end-date']

    def end_time():
        """
        The blackout end time.
        """
        return self._config['period']['end-time']
