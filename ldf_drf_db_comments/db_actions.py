"""
    REST API Documentation for the NRS TFRS Credit Trading Application

    The Transportation Fuels Reporting System is being designed to streamline
    compliance reporting for transportation fuel suppliers in accordance with
    the Renewable & Low Carbon Fuel Requirements Regulation.

    OpenAPI spec version: v1


    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.db import connection, ProgrammingError

_exception_message = 'Caught a database exception while updating comments. ' \
                     'If you are reverting a migration, you can ignore this safely.'


def create_db_comments(table_name, table_comment, column_comments=None):
    """Populate comments for non-model tables (like Django-specific tables)"""

    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'comment on table "{}" is %s'.format(table_name), [table_comment]
            )
        except ProgrammingError:
            print(_exception_message)

        if column_comments is not None:
            for column, comment in column_comments.items():
                try:
                    cursor.execute(
                        'comment on column "{}"."{}" is %s'.format(table_name, column), [comment]
                    )
                except ProgrammingError as e:
                    print('{} -- {}'.format(_exception_message, e))


def create_db_comments_from_models(models):
    """Populate comments for model tables"""

    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        for model_class in models:
            table = model_class.db_table_name() \
                if hasattr(model_class, 'db_table_name') else None
            table_comment = model_class.db_table_comment_or_name() \
                if hasattr(model_class, 'db_table_comment_or_name') else None
            column_comments = model_class.db_column_comments() \
                if hasattr(model_class, 'db_column_comments') else None

            if table_comment is not None:
                try:
                    cursor.execute(
                        'comment on table "{}" is %s'.format(table), [table_comment]
                    )
                except ProgrammingError as e:
                    print('{} -- {}'.format(_exception_message, e))

            if column_comments is not None:
                for column, comment in column_comments.items():
                    try:
                        if comment is not None:
                            cursor.execute(
                                'comment on column "{}"."{}" is %s'.format(table, column), [comment]
                            )
                    except ProgrammingError as e:
                        print('{} -- {}'.format(_exception_message, e))
