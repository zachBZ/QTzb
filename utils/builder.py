from utils.registry import Registry, build_from_cfg

RULES = Registry('rules')
DATATYPES = Registry('data_types')

def build(cfg, registry, K):
    """Build a module.

    Args:
        cfg (dict, list[dict]): The config of modules, is is either a dict
            or a list of configs.
        registry (:obj:`Registry`): A registry the module belongs to.
        default_args (dict, optional): Default arguments to build the module.
            Defaults to None.

    Returns:
        nn.Module: A built nn module.
    """
    ret = []
    for name, args in cfg[K].items():
        ret.append(build_from_cfg({"type": name}, registry, args))
    return ret


def build_rules(cfg):
    """Build backbone."""
    return build(cfg, RULES, "rules")

def build_datatypes(cfg):
    return build(cfg, DATATYPES, "data_types")

