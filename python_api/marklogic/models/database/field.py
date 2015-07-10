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
# Norman Walsh      05/10/2015     Initial development

# FIXME: how should the relationship between fields and field-range-indexes
# be modeled?

"""
Classes for dealing with fields.
"""

from marklogic.models.utilities.validators import assert_list_of_type, assert_boolean
from marklogic.models.utilities.utilities import PropertyLists

class _IncludedExcludedElement:
    """
    An included or excluded element. This class is abstract.
    """
    def __init__(self):
        raise ValueError("Do not instantiate _IncludedExcludedElement directly")

    def namespace_uri(self):
        """
        The namespace URI"
        """
        return self._config['namespace-uri']

    def set_namespace_uri(self, namespace_uri):
        """
        Set the namespace URI.
        """
        self._config['namespace-uri'] = namespace_uri
        return self

    def localname(self):
        """
        The localname.
        """
        return self._config['localname']

    def set_localname(self, localname):
        """
        Set the localname.
        """
        self._config['localname'] = localname
        return self

    def weight(self):
        """
        The weight.
        """
        return self._config['weight']

    def set_weight(self, weight):
        """
        Set the weight.
        """
        self._config['weight'] = weight
        return self

    def attribute_namespace_uri(self):
        """
        The attribute namespace URI.
        """
        return self._config['attribute-namespace-uri']

    def set_attribute_namespace_uri(self, attribute_namespace_uri):
        """
        Set the attribute namespace URI.
        """
        self._config['attribute-namespace-uri'] = attribute_namespace_uri
        return self

    def attribute_localname(self):
        """
        The attribute localname.
        """
        return self._config['attribute-localname']

    def set_attribute_localname(self, attribute_localname):
        """
        Set the attribute localname.
        """
        self._config['attribute-localname'] = attribute_localname
        return self

    def attribute_value(self):
        """
        The attribute value.
        """
        return self._config['attribute-value']

    def set_attribute_value(self, attribute_value):
        """
        Set the attribute value.
        """
        self._config['attribute-value'] = attribute_value
        return self

class IncludedElement(_IncludedExcludedElement):
    """
    An included element.
    """
    def __init__(self, namespace_uri, localname, weight=1.0,
                 attribute_namespace_uri=None,
                 attribute_localname=None,
                 attribute_value=None):
        """
        Create an included element.
        """
        # FIXME: check for attribute ns/local/value errors
        self._config = {
            "namespace-uri": namespace_uri,
            "localname": localname,
            "weight": weight,
            "attribute-namespace-uri": \
              "" if attribute_namespace_uri is None else attribute_namespace_uri,
            "attribute-localname": \
              "" if attribute_localname is None else attribute_localname,
            "attribute-value": "" if attribute_value is None else attribute_value
            }

class ExcludedElement(_IncludedExcludedElement):
    """
    An excluded element.
    """
    def __init__(self, namespace_uri, localname,
                 attribute_namespace_uri=None,
                 attribute_localname=None,
                 attribute_value=None):
        """
        Create an excluded element.
        """
        # FIXME: check for attribute ns/local/value errors
        self._config = {
            "namespace-uri": namespace_uri,
            "localname": localname,
            "attribute-namespace-uri": \
              "" if attribute_namespace_uri is None else attribute_namespace_uri,
            "attribute-localname": \
              "" if attribute_localname is None else attribute_localname,
            "attribute-value": "" if attribute_value is None else attribute_value
            }

class TokenizerOverride:
    """
    A tokenizer override.
    """
    def __init__(self, character, tokenizer_class):
        """
        Instantiate a tokenizer override.
        """
        # FIXME: check classes
        self._config = {
            "character": character,
            "tokenizer-class": tokenizer_class
            }

    def character(self):
        """
        The character.
        """
        return self._config['character']

    def set_character(self, character):
        """
        Set the character.
        """
        self._config['character'] = character
        return self

    def tokenizer_override(self):
        """
        The override class.
        """
        return self._config['tokenizer-override']

    def set_tokenizer_override(self, override):
        """
        Set the overide class.
        """
        self._config['tokenizer-override'] = override
        return self

class FieldPath:
    """
    A field path.
    """
    def __init__(self, path, weight):
        """
        Initialize a field path.
        """
        self._config = {
            "path": path,
            "weight": weight
            }

    def path(self):
        """
        The path.
        """
        return self._config['path']

    def set_path(self, path):
        """
        Set the path.
        """
        self._config['path'] = path
        return self

    def weight(self):
        """
        The weight.
        """
        return self._config['weight']

    def set_weight(self, weight):
        """
        Set the weight.
        """
        self._config['weight'] = weight
        return self

class Field(PropertyLists):
    """
    A field. This class is abstract.
    """
    def __init__(self):
        raise ValueError("Do not instantiate Field directly")

    def field_name(self):
        """
        The field name.
        """
        return self._config['field-name']

    def set_field_name(self, name):
        """
        Set the field name.
        """
        if name is None or not name:
            raise ValidationError('Fields must have a non-empty name', name)
        self._config['field-name'] = name
        return self

    def word_lexicons(self):
        """
        Word lexicons.
        """
        if 'word-lexicon' in self._config:
            return self._config['word-lexicon']
        return None

    def add_word_lexicons(self, collation):
        """
        Add a word lexicon.
        """
        return self.add_to_property_list('word-lexicon', collation)

    def set_word_lexicons(self, collations):
        """
        Set the list of word lexicons
        """
        return self.set_property_list('word-lexicon', collations)

    def remove_word_lexicons(self, collation):
        """
        Remove a word lexicon.
        """
        return self.remove_from_property_list('word-lexicon', collation)

    def included_elements(self):
        """
        The included elements.
        """
        if 'included-element' in self._config:
            return self._config['included-element']
        return None

    def add_included_element(self, element):
        """
        Add an included element.
        """
        return self.add_to_property_list('included-element',
                                         element, IncludedElement)

    def remove_included_element(self, element):
        """
        Remove an included element.
        """
        return self.remove_from_property_list('included-element',
                                              element, IncludedElement)

    def set_included_elements(self, elements):
        """
        Set the included elements.
        """
        return self.set_property_list('included-element', elements,
                                      IncludedElement)

    def excluded_elements(self):
        """
        The excluded elements.
        """
        if 'excluded-element' in self._config:
            return self._config['excluded-element']
        return None

    def add_excluded_element(self, element):
        """
        Add an excluded element.
        """
        return self.add_to_property_list('excluded-element',
                                         element, ExcludedElement)

    def remove_excluded_element(self, element):
        """
        Remove an excluded element.
        """
        return self.remove_from_property_list('excluded-element',
                                              element, ExcludedElement)

    def set_excluded_elements(self, elements):
        """
        Set the excluded elements.
        """
        return self.set_property_list('excluded-element', elements,
                                      ExcludedElement)

    def tokenizer_overrides(self):
        """
        The tokenizer overrides.
        """
        if 'tokenizer-override' in self._config:
            return self._config['tokenizer-override']
        return None

    def add_tokenizer_overrides(self, override):
        """
        Add a tokenizer override.
        """
        return self.add_to_property_list('tokenizer-override', overide,
                                         TokenizerOverride)

    def remove_tokenizer_overrides(self, override):
        """
        Remove a tokenizer override.
        """
        return self.remove_from_property_list('tokenizer-override', overide,
                                              TokenizerOverride)

    def set_tokenizer_overrides(self, overrides):
        """
        Set the list of tokenizer overrides.
        """
        return self.set_property_list('tokenizer-override', overides,
                                      TokenizerOverride)

    def stemmed_searches(self):
        """
        Stemmed searches.
        """
        if 'stemmed-searches' in self._config:
            return self._config['stemmed-searches']
        return None

    def set_stemmed_searches(self, stemmed_searches):
        """
        Set stemmed searches.
        """
        self._config['stemmed-searches'] = stemmed_searches
        return self

    def word_searches(self):
        """
        Word searches.
        """
        if 'word-searches' in self._config:
            return self._config['word-searches']
        return None

    def set_word_searches(self, word_searches):
        """
        Set word searches.
        """
        self._config['word-searches'] = assert_boolean(word_searches)
        return self

    def field_value_searches(self):
        """
        Field value searches.
        """
        if 'field-value-searches' in self._config:
            return self._config['field-value-searches']
        return None

    def set_field_value_searches(self, field_value_searches):
        """
        Set field value searches.
        """
        self._config['field-value-searches'] = assert_boolean(field_value_searches)
        return self

    def field_value_positions(self):
        """
        Field value positions.
        """
        if 'field-value-positions' in self._config:
            return self._config['field-value-positions']
        return None

    def set_field_value_positions(self, field_value_positions):
        """
        Set field value positions.
        """
        self._config['field-value-positions'] = assert_boolean(field_value_positions)
        return self

    def fast_phrase_searches(self):
        """
        Fast phrase searches.
        """
        if 'fast-phrase-searches' in self._config:
            return self._config['fast-phrase-searches']
        return None

    def set_fast_phrase_searches(self, fast_phrase_searches):
        """
        Set fast phrase searches.
        """
        self._config['fast-phrase-searches'] = assert_boolean(fast_phrase_searches)
        return self

    def fast_case_sensitive_searches(self):
        """
        Fast case-sensitive searches.
        """
        if 'fast-case-sensitive-searches' in self._config:
            return self._config['fast-case-sensitive-searches']
        return None

    def set_fast_case_sensitive_searches(self, fast_case_sensitive_searches):
        """
        Set fast case-sensitive searches.
        """
        self._config['fast-case-sensitive-searches'] = assert_boolean(fast_case_sensitive_searches)
        return self

    def fast_diacritic_sensitive_searches(self):
        """
        Fast diacritic-sensitive searches.
        """
        if 'fast-diacritic-sensitive-searches' in self._config:
            return self._config['fast-diacritic-sensitive-searches']
        return None

    def set_fast_diacritic_sensitive_searches(self, fdss):
        """
        Set fast diacritic-sensitive searches
        """
        self._config['fast-diacritic-sensitive-searches'] = assert_boolean(fdss)
        return self

    def trailing_wildcard_searches(self):
        """
        Trailing wildcard searches.
        """
        if 'trailing_wildcard_searches' in self._config:
            return self._config['trailing-wildcard-searches']
        return None

    def set_trailing_wildcard_searches(self, trailing_wildcard_searches):
        """
        Set trailing wildcard searches.
        """
        self._config['trailing-wildcard-searches'] = assert_boolean(trailing_wildcard_searches)
        return self

    def trailing_wildcard_word_positions(self):
        """
        Trailing wildcard word positions.
        """
        if 'trailing_wildcard_word_positions' in self._config:
            return self._config['trailing-wildcard-word-positions']
        return None

    def set_trailing_wildcard_word_positions(self, trailing_wildcard_word_positions):
        """
        Set trailing wildcard word positions.
        """
        self._config['trailing-wildcard-word-positions'] = assert_boolean(trailing_wildcard_word_positions)
        return self

    def three_character_searches(self):
        """
        Three character searches.
        """
        if 'three_character_searches' in self._config:
            return self._config['three-character-searches']
        return None

    def set_three_character_searches(self, three_character_searches):
        """
        Set three character searches.
        """
        self._config['three-character-searches'] = assert_boolean(three_character_searches)
        return self

    def three_character_word_positions(self):
        """
        Three character word positions.
        """
        if 'three_character_word_positions' in self._config:
            return self._config['three-character-word-positions']
        return None

    def set_three_character_word_positions(self, three_character_word_positions):
        """
        Set three character word positions.
        """
        self._config['three-character-word-positions'] = assert_boolean(three_character_word_positions)
        return self

    def two_character_searches(self):
        """
        Two character searches.
        """
        if 'two_character_searches' in self._config:
            return self._config['two-character-searches']
        return None

    def set_two_character_searches(self, two_character_searches):
        """
        Set two character searches.
        """
        self._config['two-character-searches'] = assert_boolean(two_character_searches)
        return self

    def one_character_searches(self):
        """
        One character searches.
        """
        if 'one_character_searches' in self._config:
            return self._config['one-character-searches']
        return None

    def set_one_character_searches(self, one_character_searches):
        """
        Set one character searches.
        """
        self._config['one-character-searches'] = assert_boolean(one_character_searches)
        return self

    def unmarshal(self, field):
        """
        Construct a new field from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed field object with the specified properties.
        """
        for key in field:
            if key == 'stemmed-searches':
                self._config[key] = field[key]
            elif key == 'word-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'word-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'field-value-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'field-value-positions':
                self._config[key] = (field[key] == 'true')
            elif key == 'fast-phrase-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'fast-case-sensitive-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'fast-diacritic-sensitive-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'trailing-wildcard-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'trailing-wildcard-word-positions':
                self._config[key] = (field[key] == 'true')
            elif key == 'three-character-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'three-character-word-positions':
                self._config[key] = (field[key] == 'true')
            elif key == 'two-character-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'one-character-searches':
                self._config[key] = (field[key] == 'true')
            elif key == 'word-lexicon':
                self._config[key] = field[key]
            elif key == 'included-element':
                elems = []
                for item in field[key]:
                    elem = IncludedElement(
                        item['namespace-uri'],
                        item['localname'],
                        item['weight'],
                        item['attribute-namespace-uri'],
                        item['attribute-localname'],
                        item['attribute-value'])
                    elems.append(elem)
                self._config[key] = elems
            elif key == 'excluded-element':
                elems = []
                for item in field[key]:
                    elem = ExcludedElement(
                        item['namespace-uri'],
                        item['localname'],
                        item['attribute-namespace-uri'],
                        item['attribute-localname'],
                        item['attribute-value'])
                    elems.append(elem)
                self._config[key] = elems
            elif key == 'tokenizer-override':
                elems = []
                for item in field[key]:
                    over = TokenizerOverride(
                        item['character'],
                        item['tokenizer-class'])
                    elems.append(over)
                self._config[key] = elems
            elif (key == 'field-name'
                  or key == 'include-root'
                  or key == 'field-path'):
                pass
            else:
                raise ValueError("Unexpected key in field: {0}".format(key))

    def marshal(self):
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = { }
        for key in self._config:
            if (key == 'included-element'
                or key == 'excluded-element'
                or key == 'tokenizer-override'
                or key == 'field-path'):
                jlist = []
                for index in self._config[key]:
                    jlist.append(index._config)
                struct[key] = jlist
            else:
                struct[key] = self._config[key];
        return struct

class RootField(Field):
    """
    A root field.
    """
    def __init__(self, field_name, include_root=False, includes=None,
                 excludes=None, tokenizer_overrides=None):
        """
        Create a root field.
        """
        self._config = {
            'field-name': field_name,
            'include-root': include_root
            }

        if includes is not None:
            self.set_included_elements(includes)

        if excludes is not None:
            self.set_excluded_elements(excludes)

        if tokenizer_overrides is not None:
            self.set_tokenizer_overrides(tokenizer_overrides)


    def include_root(self):
        """
        Include the root?
        """
        return self._config['include-root']

    def set_include_root(self, name):
        """
        Set the included root.
        """
        self._config['include-root'] = name
        return self

class WordQuery(RootField):
    """
    Word query settings. In the database configuration, word query settings
    are stored as a field with an empty name. They're represented separately
    in the Python API.
    """
    def __init__(self, include_root):
        """
        Create word query settings.
        """
        self._config = {
            'field-name': "",
            'include-root': include_root
            }

    def field_name(self):
        """
        Always returns None.
        """
        return None

    def set_field_name(self, name):
        """
        Raises an error.
        """
        raise ValueError("Cannot set name on WordQuery", name)

class PathField(Field):
    """
    A path field.
    """
    def __init__(self, field_name, paths):
        """
        Create a path field.
        """
        self._config = {
            'field-name': field_name,
            'field-path': assert_list_of_type(paths, FieldPath)
            }

    def field_paths(self):
        """
        The field paths.
        """
        return self._config['field-path']

    def add_field_path(self, path):
        """
        Add a field path.
        """
        return self.add_to_property_list('field-path', path, FieldPath)

    def remove_field_path(self, path):
        """
        Remove a field path.
        """
        return self.remove_from_property_list('field-path', path, FieldPath)

    def set_field_paths(self, paths):
        """
        Set the field paths.
        """
        if paths is None or not paths:
            raise ValueError("The list of field paths cannot be empty", paths)
        return self.set_property_list('field-path', paths, FieldPath)
