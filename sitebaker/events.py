import __init__


def add_filter(name, plugin):
    """
    Add a filter (similar idea to WordPress's add_filter/action).

    \param name
        the name of the filter
    \param plugin
        the callable we'll invoke for this filter
    """

    if name not in __init__.__filters__:
        __init__.__filters__[name] = []
    __init__.__filters__[name].append(plugin)


def apply_filter(name, *args):
    """
    Run the code for a filter.

    \param name
        the name of the filter
    \param args
        the set of arguments to pass to the plugin/callable
    """
    my_args = list(args)
    rtn = None
    if name in __init__.__filters__:
        plugins = __init__.__filters__[name]
        for plugin in plugins:
            rtn = plugin(*my_args)
            if rtn:
                my_args[0] = rtn
    if not rtn:
        rtn = my_args[0]
    return rtn


def add_action(name, plugin):
    """
    Add an action (similar idea to WordPress's add_action/do_action).

    \param name
        the name of the action
    \param plugin
        the callable we'll invoke for this action
    """

    if name not in __init__.__actions__:
        __init__.__actions__[name] = []
    __init__.__actions__[name].append(plugin)


def do_action(name, *args):
    """
    Run the code for an action.

    \param name
        the name of the action
    \param args
        the set of arguments to pass to the plugin/callable
    """
    if name in __init__.__actions__:
        plugins = __init__.__actions__[name]
        for plugin in plugins:
            plugin(*args)
