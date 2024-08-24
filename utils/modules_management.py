from importlib import import_module


def load_module(module_name):
    try:
        module = import_module(f'modules.{module_name}_module')
        module_class_name = ''.join([word.capitalize() for word in module_name.split('_')]) + "Module"
        module_class = getattr(module, module_class_name)
        return module_class()
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Module '{module_name}' not found or is not correctly implemented. Please ensure it exists and has a class named '{module_class_name}'.")
