import importlib
import io
import json
import logging
import operator
import os
import re
from typing import Any, Type

import yaml

logger = logging.getLogger(__name__)
WORKSPACE = "/home/glue_user/workspace"


def yaml_tag(tag):
    def register_tag(f):
        yaml.Loader.add_multi_constructor(tag, f)
        return f
    return register_tag


def __load_node(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)


def get_enviromental_variable(variable: str) -> str:
    settings_module = importlib.import_module("common.settings")
    return os.getenv(variable, getattr(settings_module, variable))


@yaml_tag('!Substitute')
def substitute_tag(loader, tag_suffix, node):
    format_string = loader.construct_scalar(node)
    pattern = re.compile(r"\{([\.A-Za-z0-9_-]+)\}")
    substitutions = re.findall(pattern, format_string)
    result = format_string
    format_dict = {substitution: get_enviromental_variable(substitution) for substitution in substitutions}
    return result.format(**format_dict)


def load_yaml(yaml_path: str, top_node: str) -> Any:
    if isinstance(yaml_path, bytes):
        yaml_path = io.BytesIO(yaml_path)
        schema = yaml.load(yaml_path.read(), Loader=yaml.Loader)
    else:
        with open(yaml_path, mode="r") as file:
            schema = yaml.load(file.read(), Loader=yaml.Loader)
    schema = schema.get("properties")
    return schema.get(top_node) if top_node else schema


def load_configuration(args: dict[str, Any], spark_conf: str) -> Any:
    environment = os.getenv("ENVIRONMENT", args.get("environment"))
    top_node = environment if operator.eq(environment, "docker") else None
    if not os.path.exists(spark_conf):
        spark_conf = os.path.join(WORKSPACE, spark_conf)
    main_list = load_yaml(yaml_path=spark_conf, top_node=top_node)
    if isinstance(main_list, list):
        return main_list
    anchors = main_list.get("__anchors__")
    conf_list = main_list.get(environment)
    if (sink_operation := args.get("sink")) and operator.eq(sink_operation, "iceberg"):
        conf_list += anchors.get("iceberg_conf")
    return conf_list
