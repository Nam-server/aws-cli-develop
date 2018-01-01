# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0e
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import mock
import tempfile
from mock import patch, Mock, MagicMock

from awscli.testutils import unittest
from awscli.customizations.cloudformation.deployer import Deployer
from awscli.customizations.cloudformation.yamlhelper import yaml_parse, yaml_dump


class TestYaml(unittest.TestCase):

    yaml_with_tags = """
    Resource:
        Key1: !Ref Something
        Key2: !GetAtt Another.Arn
        Key3: !FooBar [!Baz YetAnother, "hello"]
        Key4: !SomeTag {"a": "1"}
        Key5: !GetAtt OneMore.Outputs.Arn
        Key6: !Condition OtherCondition
    """

    parsed_yaml_dict = {
        "Resource": {
            "Key1": {
                "Ref": "Something"
            },
            "Key2": {
                "Fn::GetAtt": ["Another", "Arn"]
            },
            "Key3": {
                "Fn::FooBar": [
                    {"Fn::Baz": "YetAnother"},
                    "hello"
                ]
            },
            "Key4": {
                "Fn::SomeTag": {
                    "a": "1"
                }
            },
            "Key5": {
                "Fn::GetAtt": ["OneMore", "Outputs.Arn"]
            },
            "Key6": {
                "Condition": "OtherCondition"
            }
        }
    }

    def test_yaml_with_tags(self):
        output = yaml_parse(self.yaml_with_tags)
        self.assertEquals(self.parsed_yaml_dict, output)

        # Make sure formatter and parser work well with each other
        formatted_str = yaml_dump(output)
        output_again = yaml_parse(formatted_str)
        self.assertEquals(output, output_again)

    def test_yaml_getatt(self):
        # This is an invalid syntax for !GetAtt. But make sure the code does not crash when we encouter this syntax
        # Let CloudFormation interpret this value at runtime
        input = """
        Resource:
            Key: !GetAtt ["a", "b"]
        """

        output = {
            "Resource": {
               "Key": {
                "Fn::GetAtt": ["a", "b"]
               }

            }
        }

        actual_output = yaml_parse(input)
        self.assertEquals(actual_output, output)

    def test_parse_json_with_tabs(self):
        template = '{\n\t"foo": "bar"\n}'
        output = yaml_parse(template)
        self.assertEqual(output, {'foo': 'bar'})

