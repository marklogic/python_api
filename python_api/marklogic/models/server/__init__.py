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
# Norman Walsh      05/01/2015     Initial development

"""
Server related classes for manipulating MarkLogic databases
"""

from abc import ABCMeta, abstractmethod
import re
import requests
import time
import json
import logging
from marklogic.models.utilities.exceptions import UnexpectedManagementAPIResponse
from marklogic.models.utilities.validators import validate_custom
from marklogic.models.utilities.utilities import PropertyLists
from marklogic.models.server.schema import Schema
from marklogic.models.server.namespace import UsingNamespace, Namespace
from marklogic.models.server.requestblackout import RequestBlackout
from marklogic.models.server.module import ModuleLocation

class Server(PropertyLists):
    """
    The Server class encapsulates a MarkLogic application server. It provides
    methods to set/get common attributes.  The use of methods will
    allow IDEs with tooling to provide auto-completion hints.

    Server is the base class for all of the actual server types:
    HttpServer, OdbcServer, XdbcServer, and WebDAVServer.
    """
    __metaclass__ = ABCMeta

    def address(self):
        """
        The server socket bind numeric internet address.

        *address* specifies the IP address for the App Server.
        """
        if 'address' in self._config:
            return self._config['address']
        return None

    def set_address(self, address):
        """
        Sets the server socket bind numeric internet address.

        *address* specifies the IP address for the App Server.
        """
        self._config['address'] = address
        return self

    def authentication(self):
        """
        The authentication scheme to use for this server

        *authentication* specifies the authentication scheme
        to use for the server.
        """
        if 'authentication' in self._config:
            return self._config['authentication']
        return None

    def set_authentication(self, authentication):
        """
        Sets the authentication scheme to use for this server

        *authentication* specifies the authentication scheme
        to use for the server.
        """
        self._config['authentication'] = authentication
        return self

    def backlog(self):
        """
        The socket listen backlog.

        *backlog* specifies the maximum number of pending connections
        allowed on the HTTP server socket.
        """
        if 'backlog' in self._config:
            return self._config['backlog']
        return None

    def set_backlog(self, backlog):
        """
        Sets the socket listen backlog.

        *backlog* specifies the maximum number of pending connections
        allowed on the HTTP server socket.
        """
        self._config['backlog'] = backlog
        return self

    def collation(self):
        """
        The default collation for queries.

        *collation* specifies the default collation for queries
        run in this appserver. This will be the collation used
        for string comparison and sorting if none is specified
        in the query.
        """
        if 'collation' in self._config:
            return self._config['collation']
        return None

    def set_collation(self, collation):
        """
        Sets the default collation for queries.

        *collation* specifies the default collation for queries
        run in this appserver. This will be the collation used
        for string comparison and sorting if none is specified
        in the query.
        """
        self._config['collation'] = collation
        return self

    def concurrent_request_limit(self):
        """
        The maximum number of concurrent requests per user.

        *concurrent request limit* specifies the maximum number
        of requests any user may have running at a specific
        time. 0 indicates no maximum.
        """
        if 'concurrent-request-limit' in self._config:
            return self._config['concurrent-request-limit']
        return None

    def set_concurrent_request_limit(self, concurrent_request_limit):
        """
        Sets the maximum number of concurrent requests per user.

        *concurrent request limit* specifies the maximum number
        of requests any user may have running at a specific
        time. 0 indicates no maximum.
        """
        self._config['concurrent-request-limit'] = concurrent_request_limit
        return self

    def debug_allow(self):
        """
        Allow debugging on this server.

        *debug-allow* specifies whether to allow requests against
        this App Server to be stopped for debugging, using
        the MarkLogic Server debugging APIs.
        """
        if 'debug-allow' in self._config:
            return self._config['debug-allow']
        return None

    def set_debug_allow(self, debug_allow):
        """
        Sets allow debugging on this server.

        *debug-allow* specifies whether to allow requests against
        this App Server to be stopped for debugging, using
        the MarkLogic Server debugging APIs.
        """
        self._config['debug-allow'] = debug_allow
        return self

    def default_xquery_version(self):
        """
        The default XQuery language version for this server.

        *default-xquery-version* specifies the default XQuery
        language for this App Server if an XQuery module does
        explicitly declare its language version.
        """
        if 'default-xquery-version' in self._config:
            return self._config['default-xquery-version']
        return None

    def set_default_xquery_version(self, default_xquery_version):
        """
        Sets the default XQuery language version for this server.

        *default-xquery-version* specifies the default XQuery
        language for this App Server if an XQuery module does
        explicitly declare its language version.
        """
        self._config['default-xquery-version'] = default_xquery_version
        return self

    def last_login_database_name(self):
        """
        The database that contains users' last login information.

        *last login* specifies the name of the database in
        which this HTTP server stores users' last login information.
        """
        if 'last-login-database' in self._config:
            return self._config['last-login-database']
        return None

    def set_last_login_database_name(self, database):
        """
        Sets the database that contains users' last login information.

        *last login* specifies the name of the database in
        which this HTTP server stores users' last login information.
        """
        self._config['last-login-database'] = database
        return self

    def display_last_login(self):
        """
        Indicates whether an appserver should display users'
        last login information.

        *display last login* specifies if the ``xdmp:display-last-login``
        API should return true or false in the ``display-last-login``
        element.
        """
        if 'display-last-login' in self._config:
            return self._config['display-last-login']
        return None

    def set_display_last_login(self, display_last_login):
        """
        Sets indicates whether an appserver should display users'
        last login information.

        *display last login* specifies if the ``xdmp:display-last-login``
        API should return true or false in the ``display-last-login``
        element.
        """
        self._config['display-last-login'] = display_last_login
        return self

    def distribute_timestamps(self):
        """
        Specifies the distribution of commit timestamps after
        updates.

        *distribute timestamps* specifies how the latest timestamp
        is distributed after updates. This affects performance
        of updates and the timeliness of read-after-write query
        results from other hosts in the group.

        When set to ``fast``, updates return as quicky as possible.
        No special timestamp notification messages are broadcasted
        to other hosts. Instead, timestamps are distributed
        to other hosts when any other message is sent. The
        maximum amount of time that could pass before other
        hosts see the timestamp is one second, because a heartbeat
        message is sent to other hosts every second.

        When set to ``strict``, updates immediately broadcast
        timestamp notification messages to every other host
        in the group. Updates do not return until their timestamp
        has been distributed. This ensures timeliness of read-after-write
        query results from other hosts in the group.
        """
        if 'distribute-timestamps' in self._config:
            return self._config['distribute-timestamps']
        return None

    def set_distribute_timestamps(self, distribute_timestamps):
        """
        Sets specifies the distribution of commit timestamps after
        updates.

        *distribute timestamps* specifies how the latest timestamp
        is distributed after updates. This affects performance
        of updates and the timeliness of read-after-write query
        results from other hosts in the group.

        When set to ``fast``, updates return as quicky as possible.
        No special timestamp notification messages are broadcasted
        to other hosts. Instead, timestamps are distributed
        to other hosts when any other message is sent. The
        maximum amount of time that could pass before other
        hosts see the timestamp is one second, because a heartbeat
        message is sent to other hosts every second.

        When set to ``strict``, updates immediately broadcast
        timestamp notification messages to every other host
        in the group. Updates do not return until their timestamp
        has been distributed. This ensures timeliness of read-after-write
        query results from other hosts in the group.
        """
        self._config['distribute-timestamps'] = distribute_timestamps
        return self

    def enabled(self):
        """
        Returns the enabled status.

        :return: The enabled status or None if it is unknown
        """
        if 'enabled' in self._config:
            return self._config['enabled']
        return None

    def set_enabled(self, enabled):
        """
        Sets the enabled status.

        :param: enabled: The enabled status, either True or False
        :return: The server object.
        """
        self._config['enabled'] = enabled
        return self

    def group_name(self):
        """
        Returns the group name.

        The group name cannot be changed.

        :return: The group name or None if it is unknown
        """
        if 'group-name' in self._config:
            return self._config['group-name']
        return None

    def internal_security(self):
        """
        Whether or not the security database is used for authentication
        and authorization.

        *internal-security* specifies whether security database
        is used for authentication and authorization if the
        user is found in the security database.
        """
        if 'internal-security' in self._config:
            return self._config['internal-security']
        return None

    def set_internal_security(self, internal_security):
        """
        Sets whether or not the security database is used for authentication
        and authorization.

        *internal-security* specifies whether security database
        is used for authentication and authorization if the
        user is found in the security database.
        """
        self._config['internal-security'] = internal_security
        return self

    def log_errors(self):
        """
        Log uncaught request processing errors to ErrorLog.txt.

        *log-errors* specifes whether to log uncaught errors
        for this App Server to the ``ErrorLog.txt`` file. This
        is useful to log exceptions that might occur on an
        App Server for later debugging.
        """
        if 'log-errors' in self._config:
            return self._config['log-errors']
        return None

    def set_log_errors(self, log_errors):
        """
        Sets log uncaught request processing errors to ErrorLog.txt.

        *log-errors* specifes whether to log uncaught errors
        for this App Server to the ``ErrorLog.txt`` file. This
        is useful to log exceptions that might occur on an
        App Server for later debugging.
        """
        self._config['log-errors'] = log_errors
        return self

    def multi_version_concurrency_control(self):
        """
        Specifies concurrency control of read-only queries.

        *multi version concurrency control* specifies how the
        latest timestamp is chosen for lock-free queries. When
        set to ``contemporaneous``, the server chooses the
        latest timestamp for which transaction is known to
        have committed, even though there still may be other
        transactions for that timestamp that have not yet fully
        committed. Queries will see more timely results, but
        may block waiting for contemporaneous transactions
        to fully commit. When set to ``nonblocking``, the server
        chooses the latest timestamp for which transactions
        are known to have committed, even though there may
        be a slightly later timestamp for which another transaction
        has committed. Queries won't block waiting for transactions,
        but they may see less timely results.
        """
        if 'multi-version-concurrency-control' in self._config:
            return self._config['multi-version-concurrency-control']
        return None

    def set_multi_version_concurrency_control(self, mvcc):
        """
        Sets specifies concurrency control of read-only queries.

        *multi version concurrency control* specifies how the
        latest timestamp is chosen for lock-free queries. When
        set to ``contemporaneous``, the server chooses the
        latest timestamp for which transaction is known to
        have committed, even though there still may be other
        transactions for that timestamp that have not yet fully
        committed. Queries will see more timely results, but
        may block waiting for contemporaneous transactions
        to fully commit. When set to ``nonblocking``, the server
        chooses the latest timestamp for which transactions
        are known to have committed, even though there may
        be a slightly later timestamp for which another transaction
        has committed. Queries won't block waiting for transactions,
        but they may see less timely results.
        """
        self._config['multi-version-concurrency-control'] = mvcc
        return self

    def output_byte_order_mark(self):
        """
        The output sequence of octets is to be preceded by
        a Byte Order Mark.

        *output-byte-order-mark* Valid values are ``yes`` or
        ``no``. This is like the "byte-order-mark" option of
        both the XSLT ``xsl:output`` instruction and the MarkLogic
        XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-byte-order-mark' in self._config:
            return self._config['output-byte-order-mark']
        return None

    def set_output_byte_order_mark(self, output_byte_order_mark):
        """
        Sets the output sequence of octets is to be preceded by
        a Byte Order Mark.

        *output-byte-order-mark* Valid values are ``yes`` or
        ``no``. This is like the "byte-order-mark" option of
        both the XSLT ``xsl:output`` instruction and the MarkLogic
        XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-byte-order-mark'] = output_byte_order_mark
        return self

    def output_cdata_section_localname(self):
        """
        Element localname or list of element localnames to
        be output as CDATA sections.

        *output-cdata-section-localname* is an element or list
        of elements to be output as CDATA sections: a space-separated
        sequence of name strings (without namespace qualifiers)
        of elements defined in the "cdata section namespace
        uri" specified above. This corresponds to the "cdata-section-elements"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        You can only configure CDATA sections in one namespace
        at the level of server defaults.
        """
        if 'output-cdata-section-localname' in self._config:
            return self._config['output-cdata-section-localname']
        return None

    def set_output_cdata_section_localname(self, output_cdata_section_localname):
        """
        Sets element localname or list of element localnames to
        be output as CDATA sections.

        *output-cdata-section-localname* is an element or list
        of elements to be output as CDATA sections: a space-separated
        sequence of name strings (without namespace qualifiers)
        of elements defined in the "cdata section namespace
        uri" specified above. This corresponds to the "cdata-section-elements"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        You can only configure CDATA sections in one namespace
        at the level of server defaults.
        """
        self._config['output-cdata-section-localname'] = output_cdata_section_localname
        return self

    def output_cdata_section_namespace_uri(self):
        """
        Namespace URI of the "cdata section localname" specified
        below.

        *output-cdata-section-namespace-uri* is used in conjunction
        with output-cdata-section-localname; it is a namespace
        URI in which elements whose text contents should be
        output as CDATA sections may be specified. You can
        only configure CDATA sections in one namespace at the
        level of server defaults.
        """
        if 'output-cdata-section-namespace-uri' in self._config:
            return self._config['output-cdata-section-namespace-uri']
        return None

    def set_output_cdata_section_namespace_uri(self, output_cdata_section_namespace_uri):
        """
        Sets namespace URI of the "cdata section localname" specified
        below.

        *output-cdata-section-namespace-uri* is used in conjunction
        with output-cdata-section-localname; it is a namespace
        URI in which elements whose text contents should be
        output as CDATA sections may be specified. You can
        only configure CDATA sections in one namespace at the
        level of server defaults.
        """
        self._config['output-cdata-section-namespace-uri'] = output_cdata_section_namespace_uri
        return self

    def output_doctype_public(self):
        """
        A public identifier to use on the emitted DOCTYPE.

        *output-doctype-public* A public identifier, which
        is the public identifier to use on the emitted DOCTYPE.
        This is like the "doctype-public" option of both the
        XSLT ``xsl:output`` instruction and the MarkLogic XQuery
        ``xdmp:output`` prolog statement.
        """
        if 'output-doctype-public' in self._config:
            return self._config['output-doctype-public']
        return None

    def set_output_doctype_public(self, output_doctype_public):
        """
        Sets a public identifier to use on the emitted DOCTYPE.

        *output-doctype-public* A public identifier, which
        is the public identifier to use on the emitted DOCTYPE.
        This is like the "doctype-public" option of both the
        XSLT ``xsl:output`` instruction and the MarkLogic XQuery
        ``xdmp:output`` prolog statement.
        """
        self._config['output-doctype-public'] = output_doctype_public
        return self

    def output_doctype_system(self):
        """
        A system identifier to use on the emitted DOCTYPE.

        *output-doctype-system* A system identifier, which
        is the system identifier to use on the emitted DOCTYPE.
        This is like the "doctype-system" option of both the
        XSLT ``xsl:output`` instruction and the MarkLogic XQuery
        ``xdmp:output`` prolog statement.
        """
        if 'output-doctype-system' in self._config:
            return self._config['output-doctype-system']
        return None

    def set_output_doctype_system(self, output_doctype_system):
        """
        Sets a system identifier to use on the emitted DOCTYPE.

        *output-doctype-system* A system identifier, which
        is the system identifier to use on the emitted DOCTYPE.
        This is like the "doctype-system" option of both the
        XSLT ``xsl:output`` instruction and the MarkLogic XQuery
        ``xdmp:output`` prolog statement.
        """
        self._config['output-doctype-system'] = output_doctype_system
        return self

    def output_encoding(self):
        """
        The default output encoding.

        *output-encoding* specifies the default output encoding
        for this App Server. This is like the "encoding" option
        of both the XSLT ``xsl:output`` instruction and the
        MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-encoding' in self._config:
            return self._config['output-encoding']
        return None

    def set_output_encoding(self, output_encoding):
        """
        Sets the default output encoding.

        *output-encoding* specifies the default output encoding
        for this App Server. This is like the "encoding" option
        of both the XSLT ``xsl:output`` instruction and the
        MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-encoding'] = output_encoding
        return self

    def output_escape_uri_attributes(self):
        """
        Apply Unicode normalization, percent-encoding, and
        HTML escaping to serialized URI attributes.

        *output-escape-uri-attributes* Valid values are ``yes``
        or ``no``. This is like the "escape-uri-attributes"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-escape-uri-attributes' in self._config:
            return self._config['output-escape-uri-attributes']
        return None

    def set_output_escape_uri_attributes(self, output_escape_uri_attributes):
        """
        Sets apply Unicode normalization, percent-encoding, and
        HTML escaping to serialized URI attributes.

        *output-escape-uri-attributes* Valid values are ``yes``
        or ``no``. This is like the "escape-uri-attributes"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-escape-uri-attributes'] = output_escape_uri_attributes
        return self

    def output_include_content_type(self):
        """
        Include the content-type declaration when serializing
        the node.

        *output-include-content-type* Include the content-type
        declaration when serializing the node. Valid values
        are ``yes`` or ``no``. This is like the "include-content-type"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-include-content-type' in self._config:
            return self._config['output-include-content-type']
        return None

    def set_output_include_content_type(self, output_include_content_type):
        """
        Sets include the content-type declaration when serializing
        the node.

        *output-include-content-type* Include the content-type
        declaration when serializing the node. Valid values
        are ``yes`` or ``no``. This is like the "include-content-type"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-include-content-type'] = output_include_content_type
        return self

    def output_include_default_attributes(self):
        """
        Specifies whether attributes defaulted with a schema
        should be included in the serialization.

        *output-include-default-attributes* Serialized output
        includes default attributes.This is like the "include-default-attributes"
        option of the MarkLogic XQuery ``xdmp:output`` prolog
        statement.
        """
        if 'output-include-default-attributes' in self._config:
            return self._config['output-include-default-attributes']
        return None

    def set_output_include_default_attributes(self, output_include_default_attributes):
        """
        Sets specifies whether attributes defaulted with a schema
        should be included in the serialization.

        *output-include-default-attributes* Serialized output
        includes default attributes.This is like the "include-default-attributes"
        option of the MarkLogic XQuery ``xdmp:output`` prolog
        statement.
        """
        self._config['output-include-default-attributes'] = output_include_default_attributes
        return self

    def output_indent(self):
        """
        Pretty-print typed XML (that is, XML for which there
        is an in-scope schema).

        *output-indent* Specifies if typed XML (that is, XML
        for which there is an in-scope schema) should be pretty-printed
        (indented). Valid values are ``yes`` or ``no``. This
        is like the "indent" option of both the XSLT ``xsl:output``
        instruction and the MarkLogic XQuery ``xdmp:output``
        prolog statement.
        """
        if 'output-indent' in self._config:
            return self._config['output-indent']
        return None

    def set_output_indent(self, output_indent):
        """
        Sets pretty-print typed XML (that is, XML for which there
        is an in-scope schema).

        *output-indent* Specifies if typed XML (that is, XML
        for which there is an in-scope schema) should be pretty-printed
        (indented). Valid values are ``yes`` or ``no``. This
        is like the "indent" option of both the XSLT ``xsl:output``
        instruction and the MarkLogic XQuery ``xdmp:output``
        prolog statement.
        """
        self._config['output-indent'] = output_indent
        return self

    def output_indent_untyped(self):
        """
        Pretty-print untyped XML (that is, XML for which there
        is no in-scope schema).

        *output-indent-untyped* Specifies if untyped XML (that
        is, XML for which there is no in-scope schema) should
        be pretty-printed (indented). Valid values are ``yes``
        or ``no``. This is like the "indent-untyped" option
        of the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-indent-untyped' in self._config:
            return self._config['output-indent-untyped']
        return None

    def set_output_indent_untyped(self, output_indent_untyped):
        """
        Sets pretty-print untyped XML (that is, XML for which there
        is no in-scope schema).

        *output-indent-untyped* Specifies if untyped XML (that
        is, XML for which there is no in-scope schema) should
        be pretty-printed (indented). Valid values are ``yes``
        or ``no``. This is like the "indent-untyped" option
        of the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-indent-untyped'] = output_indent_untyped
        return self

    def output_media_type(self):
        """
        A mimetype representing a media type.

        *output-media-type* A mimetype representing a media
        type. For example, ``text/plain`` or ``text/xml`` (or
        other valid mimetypes). This is like the "media-type"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-media-type' in self._config:
            return self._config['output-media-type']
        return None

    def set_output_media_type(self, output_media_type):
        """
        Sets a mimetype representing a media type.

        *output-media-type* A mimetype representing a media
        type. For example, ``text/plain`` or ``text/xml`` (or
        other valid mimetypes). This is like the "media-type"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-media-type'] = output_media_type
        return self

    def output_method(self):
        """
        Output method.

        *output-method* Valid values are ``xml``, ``html``,
        ``xhtml``, and ``text``. This is like the "method"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-method' in self._config:
            return self._config['output-method']
        return None

    def set_output_method(self, output_method):
        """
        Sets output method.

        *output-method* Valid values are ``xml``, ``html``,
        ``xhtml``, and ``text``. This is like the "method"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-method'] = output_method
        return self

    def output_normalization_form(self):
        """
        A Unicode normalization to be applied to serialized
        output.

        *output-normalization-form* Valid values are ``NFC``,
        ``NFD``, and ``NFKD``. This is like the "normalization-form"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-normalization-form' in self._config:
            return self._config['output-normalization-form']
        return None

    def set_output_normalization_form(self, output_normalization_form):
        """
        Sets a Unicode normalization to be applied to serialized
        output.

        *output-normalization-form* Valid values are ``NFC``,
        ``NFD``, and ``NFKD``. This is like the "normalization-form"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-normalization-form'] = output_normalization_form
        return self

    def output_omit_xml_declaration(self):
        """
        Omit the XML declaration in serialized output.

        *output-omit-xml-declaration* Valid values are ``yes``
        or ``no``. This is like the "omit-xml-declaration"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-omit-xml-declaration' in self._config:
            return self._config['output-omit-xml-declaration']
        return None

    def set_output_omit_xml_declaration(self, output_omit_xml_declaration):
        """
        Sets omit the XML declaration in serialized output.

        *output-omit-xml-declaration* Valid values are ``yes``
        or ``no``. This is like the "omit-xml-declaration"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-omit-xml-declaration'] = output_omit_xml_declaration
        return self

    def output_sgml_character_entities(self):
        """
        Output SGML character entities.

        *output-sgml-character-entities* specifies whether
        to output SGML character entities for this App Server,
        and how to resolve name conflicts. Valid values are
        ``normal``, ``none``, ``math``, and ``pub``. By default
        (that is, if this option is not specified), no SGML
        entities are serialized on output, unless the App Server
        is configured to output SGML character entities.
        """
        if 'output-sgml-character-entities' in self._config:
            return self._config['output-sgml-character-entities']
        return None

    def set_output_sgml_character_entities(self, output_sgml_character_entities):
        """
        Sets output SGML character entities.

        *output-sgml-character-entities* specifies whether
        to output SGML character entities for this App Server,
        and how to resolve name conflicts. Valid values are
        ``normal``, ``none``, ``math``, and ``pub``. By default
        (that is, if this option is not specified), no SGML
        entities are serialized on output, unless the App Server
        is configured to output SGML character entities.
        """
        self._config['output-sgml-character-entities'] = output_sgml_character_entities
        return self

    def output_standalone(self):
        """
        For a value of "yes" or "no", include "standalone=<value>"
        in the XML declaration; for a value of "omit", omit
        "standalone=".

        *output-standalone* Valid values are ``yes``, ``no``,
        or ``omit``. This is like the "standalone" option of
        both the XSLT ``xsl:output`` instruction and the MarkLogic
        XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-standalone' in self._config:
            return self._config['output-standalone']
        return None

    def set_output_standalone(self, output_standalone):
        """
        Sets for a value of "yes" or "no", include "standalone=<value>"
        in the XML declaration; for a value of "omit", omit
        "standalone=".

        *output-standalone* Valid values are ``yes``, ``no``,
        or ``omit``. This is like the "standalone" option of
        both the XSLT ``xsl:output`` instruction and the MarkLogic
        XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-standalone'] = output_standalone
        return self

    def output_undeclare_prefixes(self):
        """
        Undeclare the namespace prefix of any child element
        that does not bind the prefix of its parent element.

        *output-undeclare-prefixes* Valid values are ``yes``
        or ``no``. This is like the "undeclare-prefixes" option
        of both the XSLT ``xsl:output`` instruction and the
        MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-undeclare-prefixes' in self._config:
            return self._config['output-undeclare-prefixes']
        return None

    def set_output_undeclare_prefixes(self, output_undeclare_prefixes):
        """
        Sets undeclare the namespace prefix of any child element
        that does not bind the prefix of its parent element.

        *output-undeclare-prefixes* Valid values are ``yes``
        or ``no``. This is like the "undeclare-prefixes" option
        of both the XSLT ``xsl:output`` instruction and the
        MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-undeclare-prefixes'] = output_undeclare_prefixes
        return self

    def output_version(self):
        """
        Optionally stipulate conformance to a specific version
        of the output method.

        *output-version* Valid values are ``1.0`` (for XML
        or XHTML) or ``4.0`` (for HTML). This is like the "version"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        if 'output-version' in self._config:
            return self._config['output-version']
        return None

    def set_output_version(self, output_version):
        """
        Sets optionally stipulate conformance to a specific version
        of the output method.

        *output-version* Valid values are ``1.0`` (for XML
        or XHTML) or ``4.0`` (for HTML). This is like the "version"
        option of both the XSLT ``xsl:output`` instruction
        and the MarkLogic XQuery ``xdmp:output`` prolog statement.
        """
        self._config['output-version'] = output_version
        return self

    def port(self):
        """
        The server socket bind internet port number.

        *port* specifes the socket port for the HTTP server.
        """
        if 'port' in self._config:
            return self._config['port']
        return None

    def set_port(self, port):
        """
        Sets the server socket bind internet port number.

        *port* specifes the socket port for the HTTP server.
        """
        self._config['port'] = port
        return self

    def pre_commit_trigger_depth(self):
        """
        The maximum depth of pre-commit trigger invocation.

        *pre-commit trigger limit* specifies the maximum number
        of pre-commit triggers a single statement against this
        App Server can invoke.
        """
        if 'pre-commit-trigger-depth' in self._config:
            return self._config['pre-commit-trigger-depth']
        return None

    def set_pre_commit_trigger_depth(self, pre_commit_trigger_depth):
        """
        Sets the maximum depth of pre-commit trigger invocation.

        *pre-commit trigger limit* specifies the maximum number
        of pre-commit triggers a single statement against this
        App Server can invoke.
        """
        self._config['pre-commit-trigger-depth'] = pre_commit_trigger_depth
        return self

    def pre_commit_trigger_limit(self):
        """
        The maximum number of triggers a single statement can
        invoke.

        *pre-commit trigger depth* specifies the maximum depth
        (how many triggers can cause other triggers to fire,
        which in turn cause others to fire, and so on) for
        pre-commit triggers that are executed against this
        App Server.
        """
        if 'pre-commit-trigger-limit' in self._config:
            return self._config['pre-commit-trigger-limit']
        return None

    def set_pre_commit_trigger_limit(self, pre_commit_trigger_limit):
        """
        Sets the maximum number of triggers a single statement can
        invoke.

        *pre-commit trigger depth* specifies the maximum depth
        (how many triggers can cause other triggers to fire,
        which in turn cause others to fire, and so on) for
        pre-commit triggers that are executed against this
        App Server.
        """
        self._config['pre-commit-trigger-limit'] = pre_commit_trigger_limit
        return self

    def profile_allow(self):
        """
        Allow profiling on this server.

        *profile-allow* specifies whether to allow requests
        against this App Server to be profiled, using the MarkLogic
        Server profiling APIs.
        """
        if 'profile-allow' in self._config:
            return self._config['profile-allow']
        return None

    def set_profile_allow(self, profile_allow):
        """
        Sets allow profiling on this server.

        *profile-allow* specifies whether to allow requests
        against this App Server to be profiled, using the MarkLogic
        Server profiling APIs.
        """
        self._config['profile-allow'] = profile_allow
        return self

    def root(self):
        """
        The root document directory pathname.

        *root* specifies the root directory for the web applications
        search path.

        *root* specifies the modules root directory.
        """
        if 'root' in self._config:
            return self._config['root']
        return None

    def set_root(self, root):
        """
        Sets the root document directory pathname.

        *root* specifies the root directory for the web applications
        search path.

        *root* specifies the modules root directory.
        """
        self._config['root'] = root
        return self

    def server_name(self):
        """
        The server name.

        :return: The server name
        """
        # Can't be unknown, right?
        return self._config['server-name']

    def set_server_name(self, server_name):
        """
        Set the server name.

        :param: server_name: The new server name
        :return: The server object
        """
        self._config['server-name'] = server_name
        return self

    def server_type(self):
        """
        The server type.

        The server type cannot be changed.

        :return: The server type
        """
        # Can't be unknown, right?
        return self._config['server-type']

    def ssl_allow_sslv3(self):
        """
        Whether or not SSLv3 is allowed.

        *SSL enabled* specifies whether SSLv3 is allowed for
        this XDQP.
        """
        if 'ssl-allow-sslv3' in self._config:
            return self._config['ssl-allow-sslv3']
        return None

    def set_ssl_allow_sslv3(self, ssl_allow_sslv3):
        """
        Sets whether or not SSLv3 is allowed.

        *SSL enabled* specifies whether SSLv3 is allowed for
        this XDQP.
        """
        self._config['ssl-allow-sslv3'] = ssl_allow_sslv3
        return self

    def ssl_allow_tls(self):
        """
        Whether or not TLS is allowed.

        *SSL enabled* specifies whether TLS is allowed for
        XDQP.
        """
        if 'ssl-allow-tls' in self._config:
            return self._config['ssl-allow-tls']
        return None

    def set_ssl_allow_tls(self, ssl_allow_tls):
        """
        Sets whether or not TLS is allowed.

        *SSL enabled* specifies whether TLS is allowed for
        XDQP.
        """
        self._config['ssl-allow-tls'] = ssl_allow_tls
        return self

    def ssl_certificate_template(self):
        """
        The certificate template. When a certificate template
        is specified, the App Server uses an SSL encrypted
        protocol (e.g. https, davs, xccs). The certificate
        template specifies the common information for the individual
        SSL certificates needed for each host in the group.
        You can add a new certificate template by navigating
        to Security > Certificate Templates > Create

        *ssl certificate template* specifies the certificate
        template for the App Server. When a certificate template
        is specified, the App Server uses an SSL encrypted
        protocol (e.g. https, davs, xccs). The certificate
        template specifies the common information for the individual
        SSL certificates needed for each host in the group.
        """
        if 'ssl-certificate-template' in self._config:
            return self._config['ssl-certificate-template']
        return None

    def set_ssl_certificate_template(self, ssl_certificate_template):
        """
        Sets the certificate template. When a certificate template
        is specified, the App Server uses an SSL encrypted
        protocol (e.g. https, davs, xccs). The certificate
        template specifies the common information for the individual
        SSL certificates needed for each host in the group.
        You can add a new certificate template by navigating
        to Security > Certificate Templates > Create

        *ssl certificate template* specifies the certificate
        template for the App Server. When a certificate template
        is specified, the App Server uses an SSL encrypted
        protocol (e.g. https, davs, xccs). The certificate
        template specifies the common information for the individual
        SSL certificates needed for each host in the group.
        """
        self._config['ssl-certificate-template'] = ssl_certificate_template
        return self

    def ssl_ciphers(self):
        """
        A colon separated list of ciphers (e.g. ALL:!LOW:@STRENGTH)

        *ssl ciphers* specifies the SSL ciphers that may be
        used.
        """
        if 'ssl-ciphers' in self._config:
            return self._config['ssl-ciphers']
        return None

    def set_ssl_ciphers(self, ssl_ciphers):
        """
        Sets a colon separated list of ciphers (e.g. ALL:!LOW:@STRENGTH)

        *ssl ciphers* specifies the SSL ciphers that may be
        used.
        """
        self._config['ssl-ciphers'] = ssl_ciphers
        return self

    def ssl_hostname(self):
        """
        The host name for the server's SSL certificate. This
        is useful when many servers are running behind a load
        balancer. If not specified, each host will use a certificate
        specifying its own hostname. Note that per RFC 2459,
        hostnames must not exceed 64 characters in length.

        *ssl hostname* specifies the hostname for the server's
        SSL certificate. This is useful when many servers are
        running behind a load balancer. If not specified, each
        host will use a certificate for its own hostname.
        """
        if 'ssl-hostname' in self._config:
            return self._config['ssl-hostname']
        return None

    def set_ssl_hostname(self, ssl_hostname):
        """
        Sets the host name for the server's SSL certificate. This
        is useful when many servers are running behind a load
        balancer. If not specified, each host will use a certificate
        specifying its own hostname. Note that per RFC 2459,
        hostnames must not exceed 64 characters in length.

        *ssl hostname* specifies the hostname for the server's
        SSL certificate. This is useful when many servers are
        running behind a load balancer. If not specified, each
        host will use a certificate for its own hostname.
        """
        self._config['ssl-hostname'] = ssl_hostname
        return self

    def ssl_require_client_certificate(self):
        """
        Whether or not a client certificate is required. This
        only has an effect when one or more more client certificate
        authorities are specified, in which case a value of
        true will refuse a client request if it does not present
        a valid client certificate.

        *ssl require client certificate* specifies whether
        a client certificate is required when connecting to
        this application server.
        """
        if 'ssl-require-client-certificate' in self._config:
            return self._config['ssl-require-client-certificate']
        return None

    def set_ssl_require_client_certificate(self, ssl_require_client_certificate):
        """
        Sets whether or not a client certificate is required. This
        only has an effect when one or more more client certificate
        authorities are specified, in which case a value of
        true will refuse a client request if it does not present
        a valid client certificate.

        *ssl require client certificate* specifies whether
        a client certificate is required when connecting to
        this application server.
        """
        self._config['ssl-require-client-certificate'] = ssl_require_client_certificate
        return self

    def threads(self):
        """
        The maximum number of server threads allowed.

        *threads* specifies the maximum number of App Server
        threads.
        """
        if 'threads' in self._config:
            return self._config['threads']
        return None

    def set_threads(self, threads):
        """
        Sets the maximum number of server threads allowed.

        *threads* specifies the maximum number of App Server
        threads.
        """
        self._config['threads'] = threads
        return self

    def schemas(self):
        """
        The schema binding specifications.

        :return: The schema bindings or None if there aren't any.
        """
        if 'schema' in self._config:
            return self._config['schema']
        return None

    def add_schema(self, schema):
        """
        Add a schema binding.
        """
        return self.add_to_property_list('schema', schema, Schema)

    def set_schemas(self, schemas):
        """
        Set the schema bindings
        """
        return self.set_property_list('schema', schemas, Schema)

    def remove_schema(self, schema):
        """
        Remove a schema binding.
        """
        return self.remove_from_property_list('schema', schema, Schema)

    def namespaces(self):
        """
        The namespace bindings.
        """
        if 'namespace' in self._config:
            return self._config['namespace']
        return None

    def add_namespace(self, namespace):
        """
        Add a namespace binding.
        """
        return self.add_to_property_list('namespace', namespace, Namespace)

    def set_namespaces(self, namespaces):
        """
        Set the namespace bindings.
        """
        return self.set_property_list('namespace', namespaces, Namespace)

    def remove_namespace(self, remove_ns):
        """
        Remove a namespace binding.
        """
        return self.remove_from_property_list('namespace', remove_ns, Namespace)

    def using_namespaces(self):
        """
        The namespace path URIs.
        """
        if 'using-namespaces' in self._config:
            return self._config['using-namespace']
        return None

    def add_using_namespace(self, namespace):
        """
        Add a namespace path URI.
        """
        return self.add_to_property_list('using-schema', namespace, UsingNamespace)

    def set_using_namespaces(self, using_ns):
        """
        Set the namespace path URIs.
        """
        return self.set_property_list('using-namespace', using_ns, UsingNamespace)

    def remove_using_namespaces(self, removens):
        """
        Remove a namespace path URI.
        """
        return self.remove_from_property_list('using-namespace',
                                              removens, UsingNamespace)

    def module_locations(self):
        """
        The module locations.
        """
        if 'module-location' in self._config:
            return self._config['module-location']
        return None

    def add_module_location(self, location):
        """
        Add a module location.
        """
        return self.add_to_property_list('module-location',
                                         location, ModuleLocation)

    def set_module_locations(self, locations):
        """
        Set the module locations.
        """
        return self.set_property_list('module-locations', locations, ModuleLocation)

    def request_blackouts(self):
        """
        The request blackout periods.
        """
        if 'request-blackout' in self._config:
            return self._config['request-blackout']
        else:
            return None

    def add_request_blackout(self, blackout):
        """
        Add a request blackout period.
        """
        return self.add_to_property_list('request-blackout',
                                         blackout, RequestBlackout)

    def set_request_blackouts(self, blackouts):
        """
        Set the list of request blackout periods.
        """
        return self.set_property_list('request-blackout',
                                      blackouts, RequestBlackout)

    def create(self, connection):
        """
        Creates a server on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The server object
        """
        uri = "http://{0}:{1}/manage/v2/servers" \
          .format(connection.host, connection.management_port)

        response = requests.post(uri, json=self._config, auth=connection.auth)
        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return self

    def read(self, connection):
        """
        Loads the server from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The server object
        """
        server = Server.lookup(connection, self.server_name(), self.group_name())
        if server is None:
            return None
        else:
            self._config = server._config
            self.etag = server.etag
            return self

    def update(self, connection):
        """
        Updates the server on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The server object
        """
        uri = "http://{0}:{1}/manage/v2/servers/{2}/properties?group-id={3}" \
          .format(connection.host, connection.management_port,
                  self.name, self.group_name())

        headers = {}
        if self.etag is not None:
            headers['if-match'] = self.etag

        struct = self.marshal()
        response = requests.put(uri, json=struct, auth=connection.auth,
                                headers=headers)

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        self.name = self._config['server-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        if response.status_code == 202:
            Server.wait_for_restart(connection, response)

        return self

    def delete(self, connection):
        """
        Deletes the server on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The server object
        """
        uri = "http://{0}:{1}/manage/v2/servers/{2}?group-id={3}" \
          .format(connection.host, connection.management_port,
                  self.server_name(), self.group_name())

        headers = {'accept': 'application/json'}
        if self.etag is not None:
            headers['if-match'] = self.etag

        response = requests.delete(uri, auth=connection.auth, headers=headers)

        if response.status_code > 299 and not response.status_code == 404:
            raise UnexpectedManagementAPIResponse(response.text)

        if response.status_code == 202:
            Server.wait_for_restart(connection, response)

        return self

    @classmethod
    def list(cls, connection):
        """
        List the names of all the servers on the system. Server
        names are structured values, they consist of the group name and
        the server name separated by "|".

        :param connection: The connection to a MarkLogic server

        :return: A list of servers
        """
        uri = "http://{0}:{1}/manage/v2/servers" \
          .format(connection.host, connection.port)

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['server-default-list']['list-items']['list-item']:
            results.append("{0}|{1}" \
                           .format(item['groupnameref'], item['nameref']))

        return results

    @classmethod
    def exists(cls, connection, name, group="Default"):
        """
        Returns true if (and only if) the server exists. The server
        name may be a structured value consisting of the name of the group
        and the name of the server separated by "|". If a structured name
        is used the group parameter is ignored.

        :param name: The server name
        :param group: The group name
        :param: connection: The connection to a MarkLogic server
        :return: True or False
        """
        parts = name.split("|")
        if len(parts) == 1:
            pass
        elif len(parts) == 2:
            group = parts[0]
            name = parts[1]
        else:
            raise validate_custom("Unparseable server name")

        uri = "http://{0}:{1}/manage/v2/servers/{2}/properties?group-id={3}" \
          .format(connection.host, connection.management_port,
                  name, group)

        response = requests.head(uri, auth=connection.auth)

        if response.status_code > 299 and not response.status_code == 404:
            raise UnexpectedManagementAPIResponse(response.text)

        return (response.status_code == 200)

    @classmethod
    def lookup(cls, connection, name, group='Default'):
        """
        Returns a server configuration. The server
        name may be a structured value consisting of the name of the group
        and the name of the server separated by "|". If a structured name
        is used the group parameter is ignored.

        :param name: The server name
        :param group: The group name
        :param: connection: The connection to a MarkLogic server
        :return: True or False
        """
        parts = name.split("|")
        if len(parts) == 1:
            pass
        elif len(parts) == 2:
            group = parts[0]
            name = parts[1]
        else:
            raise validate_custom("Unparseable server name")

        uri = "http://{0}:{1}/manage/v2/servers/{2}/properties?group-id={3}" \
          .format(connection.host, connection.management_port, name, group)

        logging.info("Reading server configuration: {0}[{1}]" \
                     .format(name,group))

        response = requests.get(uri, auth=connection.auth,
                                headers={u'accept': u'application/json'})

        if response.status_code > 299 and not response.status_code == 404:
            raise UnexpectedManagementAPIResponse(response.text)

        result = None

        if response.status_code == 404:
            return result

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        result = Server.unmarshal(json.loads(response.text))
        if 'etag' in response.headers:
            result.etag = response.headers['etag']

        return result

    @classmethod
    def wait_for_restart(cls, connection, response):
        """
        Waits for the server to restart.

        Some operations (removing a server, changing a server's port, etc.)
        require a restart. On receipt of a 202 response from the server,
        you can pass that response to this method and it will wait until
        the server has restarted.
        """
        rconfig = json.loads(response.text)
        timestamp = rconfig['restart']['last-startup'][0]['value']
        uri = "http://localhost:8001/admin/v1/timestamp"
        waiting = True
        while waiting:
            waiting = False
            stamp = None
            try:
                response = requests.get(uri, auth=connection.auth)
                stamp = response.text
            except requests.exceptions.ConnectionError as e:
                waiting = True
                time.sleep(2)
                pass
            except http.client.BadStatusLine as e:
                waiting = True
                time.sleep(2)
                pass

            if not(waiting):
                if re.match(r"\d\d\d\d-\d\d-\d\dT", stamp):
                    waiting = (stamp <= timestamp)
                else:
                    waiting = True

    @classmethod
    def unmarshal(cls, config):
        """
        Construct a new server from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed server object with the specified properties.
        """
        name = config['server-name']
        group = config['group-name']
        root = config['root']
        port = config['port']

        result = None
        if config['server-type'] == 'http':
            result = HttpServer(name, group, port, root)
        if config['server-type'] == 'odbc':
            result = OdbcServer(name, group, port, root)
        if config['server-type'] == 'xdbc':
            result = XdbcServer(name, group, port, root)
        if config['server-type'] == 'webdav':
            result = WebDAVServer(name, group, port, root)

        if result is None:
            raise UnexpectedManagementAPIResponse("Unexpected server type")

        result._config = config
        result.name = result._config['server-name']

        olist = []
        if 'schema' in result._config:
            for index in result._config['schema']:
                temp = Schema(index['namespace-uri'], index['schema-location'])
                olist.append(temp)
        result._config['schema'] = olist

        olist = []
        if 'namespace' in result._config:
            for index in result._config['namespace']:
                temp = Namespace(index['prefix'], index['namespace-uri'])
                olist.append(temp)
        result._config['namespace'] = olist

        olist = []
        if 'using-namespace' in result._config:
            for index in result._config['using-namespace']:
                temp = UsingNamespace(index['namespace-uri'])
                olist.append(temp)
        result._config['using-namespace'] = olist

        olist = []
        if 'module-location' in result._config:
            for index in result._config['module-location']:
                temp = ModuleLocation(index['namespace-uri'], index['location'])
                olist.append(temp)
        result._config['module-location'] = olist

        olist = []
        if 'request-blackout' in result._config:
            for blackout in result._config['request-blackout']:
                temp = None
                if (blackout['blackout-type'] == 'recurring'
                    and blackout['period'] is None):
                    temp = RequestBlackout.recurringAllDay(
                        blackout['day'],
                        blackout['user'] if 'user' in blackout else None,
                        blackout['role'] if 'role' in blackout else None)
                elif (blackout['blackout-type'] == 'recurring'
                      and 'duration' in blackout['period']):
                    temp = RequestBlackout.recurringDuration(
                        blackout['day'],
                        blackout['period']['start-time'],
                        blackout['period']['duration'],
                        blackout['user'] if 'user' in blackout else None,
                        blackout['role'] if 'role' in blackout else None)
                elif (blackout['blackout-type'] == 'recurring'
                      and 'end-time' in blackout['period']):
                    temp = RequestBlackout.recurringStartEnd(
                        blackout['day'],
                        blackout['period']['start-time'],
                        blackout['period']['end-time'],
                        blackout['user'] if 'user' in blackout else None,
                        blackout['role'] if 'role' in blackout else None)
                elif (blackout['blackout-type'] == 'once'
                      and 'end-time' in blackout['period']):
                    temp = RequestBlackout.oneTimeStartEnd(
                        blackout['period']['start-date'],
                        blackout['period']['start-time'],
                        blackout['period']['end-date'],
                        blackout['period']['end-time'],
                        blackout['user'] if 'user' in blackout else None,
                        blackout['role'] if 'role' in blackout else None)
                elif (blackout['blackout-type'] == 'once'
                      and 'duration' in blackout['period']):
                    temp = RequestBlackout.oneTimeDuration(
                        blackout['period']['start-date'],
                        blackout['period']['start-time'],
                        blackout['period']['duration'],
                        blackout['user'] if 'user' in blackout else None,
                        blackout['role'] if 'role' in blackout else None)
                else:
                    raise UnexpectedManagementAPIResponse("Unparseable request blackout period")

                olist.append(temp)
        result._config['request-blackout'] = olist
        return result

    def marshal(self):
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = { }
        for key in self._config:
            if (key == 'schema'
                or key == 'namespace'
                or key == 'using-namespace'
                or key == 'module-location'
                or key == 'request-blackout'):
                jlist = []
                for index in self._config[key]:
                    jlist.append(index._config)
                struct[key] = jlist
            else:
                struct[key] = self._config[key];
        return struct

class HttpServer(Server):
    def __init__(self, name, group="Default", port=0, root='/',
                 content_db_name=None, modules_db_name=None):
        super(Server, self).__init__()
        self.name = name
        self.etag = None
        self._config = {
            'server-name': name,
            'server-type': 'http',
            'port': port,
            'root': root,
            'group-name': group
        }
        if content_db_name is not None:
            self._config['content-database'] = content_db_name
        if modules_db_name is not None:
            self._config['modules-database'] = modules_db_name

    def compute_content_length(self):
        """
        Compute content lengths for webDAV.

        *compute-content-length* specifes whether to compute
        content length when using a webDAV server.
        """
        if 'compute-content-length' in self._config:
            return self._config['compute-content-length']
        return None

    def set_compute_content_length(self, compute_content_length):
        """
        Sets compute content lengths for webDAV.

        *compute-content-length* specifes whether to compute
        content length when using a webDAV server.
        """
        self._config['compute-content-length'] = compute_content_length
        return self

    def content_database_name(self):
        """
        The database name.

        *database* specifies the database to which this App
        Server connects for query execution.
        """
        if 'content-database' in self._config:
            return self._config['content-database']
        return None

    def set_content_database_name(self, content_database):
        """
        Sets the database name.

        *database* specifies the database to which this App
        Server connects for query execution.
        """
        self._config['content-database'] = content_database
        return self

    def default_error_format(self):
        """
        The default error format for protocol errors. One of
        html,xml,json,compatiable

        *default error handler* specifies the default format
        for protocol errors for this server.
        """
        if 'default-error-format' in self._config:
            return self._config['default-error-format']
        return None

    def set_default_error_format(self, default_error_format):
        """
        Sets the default error format for protocol errors. One of
        html,xml,json,compatiable

        *default error handler* specifies the default format
        for protocol errors for this server.
        """
        self._config['default-error-format'] = default_error_format
        return self

    def default_inference_size(self):
        """
        The default inference size for a request, in megabytes.

        *default inference size* specifies the default value
        for any request's inference size.
        """
        if 'default-inference-size' in self._config:
            return self._config['default-inference-size']
        return None

    def set_default_inference_size(self, default_inference_size):
        """
        Sets the default inference size for a request, in megabytes.

        *default inference size* specifies the default value
        for any request's inference size.
        """
        self._config['default-inference-size'] = default_inference_size
        return self

    def default_time_limit(self):
        """
        The default time limit for a request, in seconds.

        *default time limit* specifies the default value for
        any request's time limit, when otherwise unspecified.
        A request can change its time limit using ``xdmp:set-request-time-limit``.
        The time limit is the default number of seconds allowed
        for servicing a query request.
        """
        if 'default-time-limit' in self._config:
            return self._config['default-time-limit']
        return None

    def set_default_time_limit(self, default_time_limit):
        """
        Sets the default time limit for a request, in seconds.

        *default time limit* specifies the default value for
        any request's time limit, when otherwise unspecified.
        A request can change its time limit using ``xdmp:set-request-time-limit``.
        The time limit is the default number of seconds allowed
        for servicing a query request.
        """
        self._config['default-time-limit'] = default_time_limit
        return self

    def default_user(self):
        """
        The user used as the default user in application level
        authentication. Using the admin user as the default
        user is equivalent to turning security off.

        *default user* only applies for application-level authentication.
        It specifies the default user who is authenticated
        (without a password) for all users accessing the server.
        Setting the default user to a user with the admin role
        effectively disables security, because everyone who
        accesses the server then has the admin role.
        """
        if 'default-user' in self._config:
            return self._config['default-user']
        return None

    def set_default_user(self, default_user):
        """
        Sets the user used as the default user in application level
        authentication. Using the admin user as the default
        user is equivalent to turning security off.

        *default user* only applies for application-level authentication.
        It specifies the default user who is authenticated
        (without a password) for all users accessing the server.
        Setting the default user to a user with the admin role
        effectively disables security, because everyone who
        accesses the server then has the admin role.
        """
        self._config['default-user'] = default_user
        return self

    def error_handler(self):
        """
        The script that handles 400 and 500 errors for this
        server.

        *error handler* specifies the page to internally redirect
        to in case of any 400 or 500 errors.
        """
        if 'error-handler' in self._config:
            return self._config['error-handler']
        return None

    def set_error_handler(self, error_handler):
        """
        Sets the script that handles 400 and 500 errors for this
        server.

        *error handler* specifies the page to internally redirect
        to in case of any 400 or 500 errors.
        """
        self._config['error-handler'] = error_handler
        return self

    def execute(self):
        """
        The execute flag
        """
        if 'execute' in self._config:
            return self._config['execute']
        return None

    def set_execute(self, execute):
        """
        Set the execute flag
        """
        self._config['execute'] = execute
        return self

    def keep_alive_timeout(self):
        """
        The keep-alive socket recv timeout, in seconds.

        *keep alive timeout* specifies the maximum number of
        seconds before a socket receives a timeout for subsequent
        requests over the same connection.
        """
        if 'keep-alive-timeout' in self._config:
            return self._config['keep-alive-timeout']
        return None

    def set_keep_alive_timeout(self, keep_alive_timeout):
        """
        Sets the keep-alive socket recv timeout, in seconds.

        *keep alive timeout* specifies the maximum number of
        seconds before a socket receives a timeout for subsequent
        requests over the same connection.
        """
        self._config['keep-alive-timeout'] = keep_alive_timeout
        return self

    def max_inference_size(self):
        """
        The upper bound for a request's inference size, in
        megabytes.

        *max inference size* specifies the upper bound for
        any request's inference size. No request may set its
        inference size higher than this number. The inference
        size, in turn, is the maximum amount of memory in megabytes
        allowed for sem:store performing inference. The App
        Server gives up on queries which exceed the memory
        limit, and returns an error.
        """
        if 'max-inference-size' in self._config:
            return self._config['max-inference-size']
        return None

    def set_max_inference_size(self, max_inference_size):
        """
        Sets the upper bound for a request's inference size, in
        megabytes.

        *max inference size* specifies the upper bound for
        any request's inference size. No request may set its
        inference size higher than this number. The inference
        size, in turn, is the maximum amount of memory in megabytes
        allowed for sem:store performing inference. The App
        Server gives up on queries which exceed the memory
        limit, and returns an error.
        """
        self._config['max-inference-size'] = max_inference_size
        return self

    def max_time_limit(self):
        """
        The upper bound for a request's time limit, in seconds.

        *max time limit* specifies the upper bound for any
        request's time limit. No request may set its time limit
        (for example with ``xdmp:set-request-time-limit``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        if 'max-time-limit' in self._config:
            return self._config['max-time-limit']
        return None

    def set_max_time_limit(self, max_time_limit):
        """
        Sets the upper bound for a request's time limit, in seconds.

        *max time limit* specifies the upper bound for any
        request's time limit. No request may set its time limit
        (for example with ``xdmp:set-request-time-limit``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        self._config['max-time-limit'] = max_time_limit
        return self

    def modules_database_name(self):
        """
        The database that contains application modules.

        *modules* specifies the name of the database in which
        this HTTP server locates XQuery application code. If
        set to (file system), then any files in the specified
        *root* directory are executable (given the proper permissions).
        If set to a database, then any documents in the database
        whose URI begins with the specified *root* directory
        are executable.
        """
        if 'modules-database' in self._config:
            return self._config['modules-database']
        return None

    def set_modules_database_name(self, modules_database):
        """
        Sets the database that contains application modules.

        *modules* specifies the name of the database in which
        this HTTP server locates XQuery application code. If
        set to (file system), then any files in the specified
        *root* directory are executable (given the proper permissions).
        If set to a database, then any documents in the database
        whose URI begins with the specified *root* directory
        are executable.
        """
        self._config['modules-database'] = modules_database
        return self

    def privilege_name(self):
        """
        The privilege restricting access to the server.

        *privilege* specifies the execute privilege required
        to access the server.
        """
        if 'privilege' in self._config:
            return self._config['privilege']
        return None

    def set_privilege_name(self, privilege):
        """
        Sets the privilege restricting access to the server.

        *privilege* specifies the execute privilege required
        to access the server.
        """
        self._config['privilege'] = privilege
        return self

    def request_timeout(self):
        """
        The request socket recv timeout, in seconds.

        *request timeout* specifies the maximum number of seconds
        before a socket receives a timeout for the first request.
        """
        if 'request-timeout' in self._config:
            return self._config['request-timeout']
        return None

    def set_request_timeout(self, request_timeout):
        """
        Sets the request socket recv timeout, in seconds.

        *request timeout* specifies the maximum number of seconds
        before a socket receives a timeout for the first request.
        """
        self._config['request-timeout'] = request_timeout
        return self

    def rewrite_resolves_globally(self):
        """
        Allow rewritten URLs to be resolved from the global
        MarkLogic Modules/ directory.

        *rewrite resolves globally* specifies whether to allow
        rewritten URLs to be resolved from the global MarkLogic
        Modules/ directory.
        """
        if 'rewrite-resolves-globally' in self._config:
            return self._config['rewrite-resolves-globally']
        return None

    def set_rewrite_resolves_globally(self, rewrite_resolves_globally):
        """
        Sets allow rewritten URLs to be resolved from the global
        MarkLogic Modules/ directory.

        *rewrite resolves globally* specifies whether to allow
        rewritten URLs to be resolved from the global MarkLogic
        Modules/ directory.
        """
        self._config['rewrite-resolves-globally'] = rewrite_resolves_globally
        return self

    def session_timeout(self):
        """
        The session expiration timeout, in seconds.

        *session timeout* specifies the maximum number of seconds
        before a session times out.
        """
        if 'session-timeout' in self._config:
            return self._config['session-timeout']
        return None

    def set_session_timeout(self, session_timeout):
        """
        Sets the session expiration timeout, in seconds.

        *session timeout* specifies the maximum number of seconds
        before a session times out.
        """
        self._config['session-timeout'] = session_timeout
        return self

    def static_expires(self):
        """
        Add an "expires" HTTP header for static content to
        expire after this many seconds.

        *static expires* adds an "expires" HTTP header for
        static content to expire after this many seconds.
        """
        if 'static-expires' in self._config:
            return self._config['static-expires']
        return None

    def set_static_expires(self, static_expires):
        """
        Sets add an "expires" HTTP header for static content to
        expire after this many seconds.

        *static expires* adds an "expires" HTTP header for
        static content to expire after this many seconds.
        """
        self._config['static-expires'] = static_expires
        return self

    def url_rewriter(self):
        """
        The script that rewrites URLs for this server.

        *url rewriter* specifies the script to run to rewrite
        URLs.
        """
        if 'url-rewriter' in self._config:
            return self._config['url-rewriter']
        return None

    def set_url_rewriter(self, url_rewriter):
        """
        Sets the script that rewrites URLs for this server.

        *url rewriter* specifies the script to run to rewrite
        URLs.
        """
        self._config['url-rewriter'] = url_rewriter
        return self

    def webDAV(self):
        """
        The webDAV setting.
        """
        if 'webDAV' in self._config:
            return self._config['webDAV']
        return None

class OdbcServer(Server):
    def __init__(self, name, group='Default', port=0, root='/',
                 content_db_name=None, modules_db_name=None):
        super(Server, self).__init__()
        self.name = name
        self.etag = None
        self._config = {
            'server-name': name,
            'server-type': 'odbc',
            'port': port,
            'root': root,
            'group-name': group
        }
        if content_db_name is not None:
            self._config['content-database'] = content_db_name
        if modules_db_name is not None:
            self._config['modules-database'] = modules_db_name

    def connection_timeout(self):
        """
        The idle connection expiration timeout, in seconds,
        or 0 to indicate no idle connection timeout.

        *connection timeout* specifies the maximum number of
        seconds in an idle state before a connection times
        out. A value of 0 means the connection will never time
        out.
        """
        if 'connection-timeout' in self._config:
            return self._config['connection-timeout']
        return None

    def set_connection_timeout(self, connection_timeout):
        """
        Sets the idle connection expiration timeout, in seconds,
        or 0 to indicate no idle connection timeout.

        *connection timeout* specifies the maximum number of
        seconds in an idle state before a connection times
        out. A value of 0 means the connection will never time
        out.
        """
        self._config['connection-timeout'] = connection_timeout
        return self

    def default_query_time_limit(self):
        """
        The default time limit for a query, in seconds.

        *default query time limit* specifies the default value
        for any query's time limit, when otherwise unspecified.
        The query timeout can be changed at runtime using the
        statement ``SET statement_timeout``. The time limit,
        in turn, is the maximum number of seconds allowed for
        servicing a query request. The App Server gives up
        on queries which take longer, and returns an error.
        """
        if 'default-query-time-limit' in self._config:
            return self._config['default-query-time-limit']
        return None

    def set_default_query_time_limit(self, default_query_time_limit):
        """
        Sets the default time limit for a query, in seconds.

        *default query time limit* specifies the default value
        for any query's time limit, when otherwise unspecified.
        The query timeout can be changed at runtime using the
        statement ``SET statement_timeout``. The time limit,
        in turn, is the maximum number of seconds allowed for
        servicing a query request. The App Server gives up
        on queries which take longer, and returns an error.
        """
        self._config['default-query-time-limit'] = default_query_time_limit
        return self

    def max_query_time_limit(self):
        """
        The upper bound for a query's time limit, in seconds.

        *max query time limit* specifies the upper bound for
        any query's time limit. No runtime statement may set
        the time limit (for example with ``SET statement_timeout``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        if 'max-query-time-limit' in self._config:
            return self._config['max-query-time-limit']
        return None

    def set_max_query_time_limit(self, max_query_time_limit):
        """
        Sets the upper bound for a query's time limit, in seconds.

        *max query time limit* specifies the upper bound for
        any query's time limit. No runtime statement may set
        the time limit (for example with ``SET statement_timeout``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        self._config['max-query-time-limit'] = max_query_time_limit
        return self

class XdbcServer(Server):
    def __init__(self, name, group='Default', port=0, root='/',
                 content_db_name=None, modules_db_name=None):
        super(Server, self).__init__()
        self.name = name
        self.etag = None
        self._config = {
            'server-name': name,
            'server-type': 'xdbc',
            'port': port,
            'root': root,
            'group-name': group
        }
        if content_db_name is not None:
            self._config['content-database'] = content_db_name
        if modules_db_name is not None:
            self._config['modules-database'] = modules_db_name

    def default_inference_size(self):
        """
        The default inference size for a request, in megabytes.

        *default inference size* specifies the default value
        for any request's inference size.
        """
        if 'default-inference-size' in self._config:
            return self._config['default-inference-size']
        return None

    def set_default_inference_size(self, default_inference_size):
        """
        Sets the default inference size for a request, in megabytes.

        *default inference size* specifies the default value
        for any request's inference size.
        """
        self._config['default-inference-size'] = default_inference_size
        return self

    def default_time_limit(self):
        """
        The default time limit for a request, in seconds.

        *default time limit* specifies the default value for
        any request's time limit, when otherwise unspecified.
        A request can change its time limit using ``xdmp:set-request-time-limit``.
        The time limit is the default number of seconds allowed
        for servicing a query request.
        """
        if 'default-time-limit' in self._config:
            return self._config['default-time-limit']
        return None

    def set_default_time_limit(self, default_time_limit):
        """
        Sets the default time limit for a request, in seconds.

        *default time limit* specifies the default value for
        any request's time limit, when otherwise unspecified.
        A request can change its time limit using ``xdmp:set-request-time-limit``.
        The time limit is the default number of seconds allowed
        for servicing a query request.
        """
        self._config['default-time-limit'] = default_time_limit
        return self

    def keep_alive_timeout(self):
        """
        The keep-alive socket recv timeout, in seconds.

        *keep alive timeout* specifies the maximum number of
        seconds before a socket receives a timeout for subsequent
        requests over the same connection.
        """
        if 'keep-alive-timeout' in self._config:
            return self._config['keep-alive-timeout']
        return None

    def set_keep_alive_timeout(self, keep_alive_timeout):
        """
        Sets the keep-alive socket recv timeout, in seconds.

        *keep alive timeout* specifies the maximum number of
        seconds before a socket receives a timeout for subsequent
        requests over the same connection.
        """
        self._config['keep-alive-timeout'] = keep_alive_timeout
        return self

    def max_inference_size(self):
        """
        The upper bound for a request's inference size, in
        megabytes.

        *max inference size* specifies the upper bound for
        any request's inference size. No request may set its
        inference size higher than this number. The inference
        size, in turn, is the maximum amount of memory in megabytes
        allowed for sem:store performing inference. The App
        Server gives up on queries which exceed the memory
        limit, and returns an error.
        """
        if 'max-inference-size' in self._config:
            return self._config['max-inference-size']
        return None

    def set_max_inference_size(self, max_inference_size):
        """
        Sets the upper bound for a request's inference size, in
        megabytes.

        *max inference size* specifies the upper bound for
        any request's inference size. No request may set its
        inference size higher than this number. The inference
        size, in turn, is the maximum amount of memory in megabytes
        allowed for sem:store performing inference. The App
        Server gives up on queries which exceed the memory
        limit, and returns an error.
        """
        self._config['max-inference-size'] = max_inference_size
        return self

    def max_time_limit(self):
        """
        The upper bound for a request's time limit, in seconds.

        *max time limit* specifies the upper bound for any
        request's time limit. No request may set its time limit
        (for example with ``xdmp:set-request-time-limit``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        if 'max-time-limit' in self._config:
            return self._config['max-time-limit']
        return None

    def set_max_time_limit(self, max_time_limit):
        """
        Sets the upper bound for a request's time limit, in seconds.

        *max time limit* specifies the upper bound for any
        request's time limit. No request may set its time limit
        (for example with ``xdmp:set-request-time-limit``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        self._config['max-time-limit'] = max_time_limit
        return self

    def request_timeout(self):
        """
        The request socket recv timeout, in seconds.

        *request timeout* specifies the maximum number of seconds
        before a socket receives a timeout for the first request.
        """
        if 'request-timeout' in self._config:
            return self._config['request-timeout']
        return None

    def set_request_timeout(self, request_timeout):
        """
        Sets the request socket recv timeout, in seconds.

        *request timeout* specifies the maximum number of seconds
        before a socket receives a timeout for the first request.
        """
        self._config['request-timeout'] = request_timeout
        return self

    def session_timeout(self):
        """
        The session expiration timeout, in seconds.

        *session timeout* specifies the maximum number of seconds
        before a session times out.
        """
        if 'session-timeout' in self._config:
            return self._config['session-timeout']
        return None

    def set_session_timeout(self, session_timeout):
        """
        Sets the session expiration timeout, in seconds.

        *session timeout* specifies the maximum number of seconds
        before a session times out.
        """
        self._config['session-timeout'] = session_timeout
        return self

class WebDAVServer(Server):
    def __init__(self, name, group='Default', port=0, root='/',
                 content_db_name=None):
        super(Server, self).__init__()
        self.name = name
        self.etag = None
        self._config = {
            'server-name': name,
            'server-type': 'webdav',
            'port': port,
            'root': root,
            'group-name': group
        }
        # Yes, modules-database is intentional here!
        if content_db_name is not None:
            self._config['modules-database'] = content_db_name

    def compute_content_length(self):
        """
        Compute content lengths for webDAV.

        *compute-content-length* specifes whether to compute
        content length when using a webDAV server.
        """
        if 'compute-content-length' in self._config:
            return self._config['compute-content-length']
        return None

    def set_compute_content_length(self, compute_content_length):
        """
        Sets compute content lengths for webDAV.

        *compute-content-length* specifes whether to compute
        content length when using a webDAV server.
        """
        self._config['compute-content-length'] = compute_content_length
        return self

    def default_error_format(self):
        """
        The default error format for protocol errors. One of
        html,xml,json,compatiable

        *default error handler* specifies the default format
        for protocol errors for this server.
        """
        if 'default-error-format' in self._config:
            return self._config['default-error-format']
        return None

    def set_default_error_format(self, default_error_format):
        """
        Sets the default error format for protocol errors. One of
        html,xml,json,compatiable

        *default error handler* specifies the default format
        for protocol errors for this server.
        """
        self._config['default-error-format'] = default_error_format
        return self

    def default_inference_size(self):
        """
        The default inference size for a request, in megabytes.

        *default inference size* specifies the default value
        for any request's inference size.
        """
        if 'default-inference-size' in self._config:
            return self._config['default-inference-size']
        return None

    def set_default_inference_size(self, default_inference_size):
        """
        Sets the default inference size for a request, in megabytes.

        *default inference size* specifies the default value
        for any request's inference size.
        """
        self._config['default-inference-size'] = default_inference_size
        return self

    def default_time_limit(self):
        """
        The default time limit for a request, in seconds.

        *default time limit* specifies the default value for
        any request's time limit, when otherwise unspecified.
        A request can change its time limit using ``xdmp:set-request-time-limit``.
        The time limit is the default number of seconds allowed
        for servicing a query request.
        """
        if 'default-time-limit' in self._config:
            return self._config['default-time-limit']
        return None

    def set_default_time_limit(self, default_time_limit):
        """
        Sets the default time limit for a request, in seconds.

        *default time limit* specifies the default value for
        any request's time limit, when otherwise unspecified.
        A request can change its time limit using ``xdmp:set-request-time-limit``.
        The time limit is the default number of seconds allowed
        for servicing a query request.
        """
        self._config['default-time-limit'] = default_time_limit
        return self

    def default_user(self):
        """
        The user used as the default user in application level
        authentication. Using the admin user as the default
        user is equivalent to turning security off.

        *default user* only applies for application-level authentication.
        It specifies the default user who is authenticated
        (without a password) for all users accessing the server.
        Setting the default user to a user with the admin role
        effectively disables security, because everyone who
        accesses the server then has the admin role.
        """
        if 'default-user' in self._config:
            return self._config['default-user']
        return None

    def set_default_user(self, default_user):
        """
        Sets the user used as the default user in application level
        authentication. Using the admin user as the default
        user is equivalent to turning security off.

        *default user* only applies for application-level authentication.
        It specifies the default user who is authenticated
        (without a password) for all users accessing the server.
        Setting the default user to a user with the admin role
        effectively disables security, because everyone who
        accesses the server then has the admin role.
        """
        self._config['default-user'] = default_user
        return self

    def error_handler(self):
        """
        The script that handles 400 and 500 errors for this
        server.

        *error handler* specifies the page to internally redirect
        to in case of any 400 or 500 errors.
        """
        if 'error-handler' in self._config:
            return self._config['error-handler']
        return None

    def set_error_handler(self, error_handler):
        """
        Sets the script that handles 400 and 500 errors for this
        server.

        *error handler* specifies the page to internally redirect
        to in case of any 400 or 500 errors.
        """
        self._config['error-handler'] = error_handler
        return self

    def execute(self):
        if 'execute' in self._config:
            return self._config['execute']
        return None

    def set_execute(self, execute):
        self._config['execute'] = execute
        return self

    def keep_alive_timeout(self):
        """
        The keep-alive socket recv timeout, in seconds.

        *keep alive timeout* specifies the maximum number of
        seconds before a socket receives a timeout for subsequent
        requests over the same connection.
        """
        if 'keep-alive-timeout' in self._config:
            return self._config['keep-alive-timeout']
        return None

    def set_keep_alive_timeout(self, keep_alive_timeout):
        """
        Sets the keep-alive socket recv timeout, in seconds.

        *keep alive timeout* specifies the maximum number of
        seconds before a socket receives a timeout for subsequent
        requests over the same connection.
        """
        self._config['keep-alive-timeout'] = keep_alive_timeout
        return self

    def max_inference_size(self):
        """
        The upper bound for a request's inference size, in
        megabytes.

        *max inference size* specifies the upper bound for
        any request's inference size. No request may set its
        inference size higher than this number. The inference
        size, in turn, is the maximum amount of memory in megabytes
        allowed for sem:store performing inference. The App
        Server gives up on queries which exceed the memory
        limit, and returns an error.
        """
        if 'max-inference-size' in self._config:
            return self._config['max-inference-size']
        return None

    def set_max_inference_size(self, max_inference_size):
        """
        Sets the upper bound for a request's inference size, in
        megabytes.

        *max inference size* specifies the upper bound for
        any request's inference size. No request may set its
        inference size higher than this number. The inference
        size, in turn, is the maximum amount of memory in megabytes
        allowed for sem:store performing inference. The App
        Server gives up on queries which exceed the memory
        limit, and returns an error.
        """
        self._config['max-inference-size'] = max_inference_size
        return self

    def max_time_limit(self):
        """
        The upper bound for a request's time limit, in seconds.

        *max time limit* specifies the upper bound for any
        request's time limit. No request may set its time limit
        (for example with ``xdmp:set-request-time-limit``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        if 'max-time-limit' in self._config:
            return self._config['max-time-limit']
        return None

    def set_max_time_limit(self, max_time_limit):
        """
        Sets the upper bound for a request's time limit, in seconds.

        *max time limit* specifies the upper bound for any
        request's time limit. No request may set its time limit
        (for example with ``xdmp:set-request-time-limit``)
        higher than this number. The time limit, in turn, is
        the maximum number of seconds allowed for servicing
        a query request. The App Server gives up on queries
        which take longer, and returns an error.
        """
        self._config['max-time-limit'] = max_time_limit
        return self

    def request_timeout(self):
        """
        The request socket recv timeout, in seconds.

        *request timeout* specifies the maximum number of seconds
        before a socket receives a timeout for the first request.
        """
        if 'request-timeout' in self._config:
            return self._config['request-timeout']
        return None

    def set_request_timeout(self, request_timeout):
        """
        Sets the request socket recv timeout, in seconds.

        *request timeout* specifies the maximum number of seconds
        before a socket receives a timeout for the first request.
        """
        self._config['request-timeout'] = request_timeout
        return self

    def rewrite_resolves_globally(self):
        """
        Allow rewritten URLs to be resolved from the global
        MarkLogic Modules/ directory.

        *rewrite resolves globally* specifies whether to allow
        rewritten URLs to be resolved from the global MarkLogic
        Modules/ directory.
        """
        if 'rewrite-resolves-globally' in self._config:
            return self._config['rewrite-resolves-globally']
        return None

    def set_rewrite_resolves_globally(self, rewrite_resolves_globally):
        """
        Sets allow rewritten URLs to be resolved from the global
        MarkLogic Modules/ directory.

        *rewrite resolves globally* specifies whether to allow
        rewritten URLs to be resolved from the global MarkLogic
        Modules/ directory.
        """
        self._config['rewrite-resolves-globally'] = rewrite_resolves_globally
        return self

    def session_timeout(self):
        """
        The session expiration timeout, in seconds.

        *session timeout* specifies the maximum number of seconds
        before a session times out.
        """
        if 'session-timeout' in self._config:
            return self._config['session-timeout']
        return None

    def set_session_timeout(self, session_timeout):
        """
        Sets the session expiration timeout, in seconds.

        *session timeout* specifies the maximum number of seconds
        before a session times out.
        """
        self._config['session-timeout'] = session_timeout
        return self

    def static_expires(self):
        """
        Add an "expires" HTTP header for static content to
        expire after this many seconds.

        *static expires* adds an "expires" HTTP header for
        static content to expire after this many seconds.
        """
        if 'static-expires' in self._config:
            return self._config['static-expires']
        return None

    def set_static_expires(self, static_expires):
        """
        Sets add an "expires" HTTP header for static content to
        expire after this many seconds.

        *static expires* adds an "expires" HTTP header for
        static content to expire after this many seconds.
        """
        self._config['static-expires'] = static_expires
        return self

    def url_rewriter(self):
        """
        The script that rewrites URLs for this server.

        *url rewriter* specifies the script to run to rewrite
        URLs.
        """
        if 'url-rewriter' in self._config:
            return self._config['url-rewriter']
        return None

    def set_url_rewriter(self, url_rewriter):
        """
        Sets the script that rewrites URLs for this server.

        *url rewriter* specifies the script to run to rewrite
        URLs.
        """
        self._config['url-rewriter'] = url_rewriter
        return self

    def webDAV(self):
        if 'webDAV' in self._config:
            return self._config['webDAV']
        return None
