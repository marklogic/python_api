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
Classes for dealing with database merge blackouts
"""

class MergeBlackout:
    """
    A merge blackout period. This is an abstract class.
    """
    def __init__(self):
        raise ValueError("Do not instantiate MergeBlackout directly")

    def blackout_type(self):
        """
        The blackout type.
        """
        return self._config['blackout_type']

    def limit(self):
        """
        The limit.
        """
        return self._config['limit']

    def merge_priority(self):
        """
        The merge priority.
        """
        return self._config['merge-priority']

    @classmethod
    def recurringDuration(cls, priority, limit, days, start_time, duration):
        """
        Create a recurring blackout with a duration.
        """
        # FIXME: validate args
        return MergeBlackoutRecurringDuration(priority,limit,days,
                                                    start_time, duration)

    @classmethod
    def recurringStartEnd(cls, priority, limit, days, start_time, end_time):
        """
        Create a recurring blackout with a start and end time.
        """
        # FIXME: validate args
        return MergeBlackoutRecurringStartEnd(priority,limit,days,
                                                    start_time, end_time)
    @classmethod
    def recurringAllDay(cls, priority, limit, days):
        """
        Create a recurring blackout that lasts all day.
        """
        # FIXME: validate args
        return MergeBlackoutRecurringAllDay(priority,limit, days)

    @classmethod
    def oneTimeDuration(cls, priority, limit, start_date, start_time, duration):
        """
        Create a one-time blackout with a duration.
        """
        # FIXME: validate args
        return MergeBlackoutOneTimeDuration(priority,limit,
                                            start_date, start_time, duration)

    @classmethod
    def oneTimeStartEnd(cls, priority, limit,
                        start_date, start_time,
                        end_date, end_time):
        """
        Create a one-time blackout with a start and end time.
        """
        # FIXME: validate args
        return MergeBlackoutOneTimeStartEnd(priority,limit,
                                            start_date, start_time,
                                            end_date, end_time)


class MergeBlackoutRecurringDuration(MergeBlackout):
    """
    A recurring merge blackout period for a duration
    """
    def __init__(self, priority, limit, days, start_time, duration):
        """
        Create a recurring merge blackout period for a duration
        """
        self._config = {
            'blackout-type': 'recurring',
            'merge-priority': priority,
            'limit': limit,
            'day': days,
            'period': {
                'start-time': start_time,
                'duration': duration
                }
            }

    def days():
        """
        The days.
        """
        return self._config['days']

    def start_time():
        """
        The start time.
        """
        return self._config['period']['start-time']

    def duration():
        """
        The duration.
        """
        return self._config['period']['duration']

class MergeBlackoutRecurringStartEnd(MergeBlackout):
    """
    A recurring merge blackout period with start and end times
    """
    def __init__(self, priority, limit, days, start_time, end_time):
        """
        Create a recurring merge blackout period with start and end times
        """
        self._config = {
            'blackout-type': "recurring",
            'merge-priority': priority,
            'limit': limit,
            'day': days,
            'period': {
                'start-time': start_time,
                'end-time': end_time
                }
            }

    def days():
        """
        The days.
        """
        return self._config['days']

    def start_time():
        """
        The start time.
        """
        return self._config['period']['start-time']

    def end_time():
        """
        The end time.
        """
        return self._config['period']['end-time']

class MergeBlackoutRecurringAllDay(MergeBlackout):
    """
    A recurring merge blackout period for a whole day
    """
    def __init__(self, priority, limit, days):
        """
        Create a recurring merge blackout period for a whole day
        """
        self._config = {
            'blackout-type': "recurring",
            'merge-priority': priority,
            'limit': limit,
            'day': days,
            'period': None
            }

    def days():
        """
        The days.
        """
        return self._config['days']

class MergeBlackoutOneTimeDuration(MergeBlackout):
    """
    A one time merge blackout period with a duration
    """
    def __init__(self, priority, limit, start_date, start_time, duration):
        """
        Create a one time merge blackout period with a duration
        """
        self._config = {
            'blackout-type': "once",
            'merge-priority': priority,
            'limit': limit,
            'period': {
                'start-date': start_date,
                'start-time': start_time,
                'duration': duration
                }
            }

    def start_date():
        """
        The start date.
        """
        return self._config['period']['start-date']

    def start_time():
        """
        The start time.
        """
        return self._config['period']['start-time']

    def duration():
        """
        The duration.
        """
        return self._config['period']['duration']


class MergeBlackoutOneTimeStartEnd(MergeBlackout):
    """
    A one time merge blackout period with start and end times
    """
    def __init__(self, priority, limit, start_date, start_time, end_date, end_time):
        """
        Create a one time merge blackout period with start and end times
        """
        self._config = {
            'blackout-type': "once",
            'merge-priority': priority,
            'limit': limit,
            'period': {
                'start-date': start_date,
                'start-time': start_time,
                'end-date': end_date,
                'end-time': end_time,
                }
            }

    def start_date():
        """
        The start date.
        """
        return self._config['period']['start-date']

    def start_time():
        """
        The start time.
        """
        return self._config['period']['start-time']

    def end_date():
        """
        The end date.
        """
        return self._config['period']['end-date']

    def end_time():
        """
        The end time.
        """
        return self._config['period']['end-time']
