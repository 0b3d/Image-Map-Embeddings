import importlib
from visualizations.base_visualizer import BaseVisualizer

def find_visualizer_using_name(visualizer_name):
    """Import the module "data/[dataset_name]_visualizer.py".

    In the file, the class called VisualizerNameVisualizer() will
    be instantiated. It has to be a subclass of BaseVisualizer,
    and it is case-insensitive.
    """
    visualizer_filename = "visualizations." + visualizer_name + "_visualizer"
    datasetlib = importlib.import_module(visualizer_filename)

    visualizer = None
    target_visualizer_name = visualizer_name.replace('_', '') + 'visualizer'
    for name, cls in datasetlib.__dict__.items():
        if name.lower() == target_visualizer_name.lower() \
           and issubclass(cls, BaseVisualizer):
            visualizer = cls

    if visualizer is None:
        raise NotImplementedError("In %s.py, there should be a subclass of BaseVisualizer with class name that matches %s in lowercase." % (visualizer_filename, target_visualizer_name))

    return visualizer


def get_option_setter(visualizer_name):
    """Return the static method <modify_commandline_options> of the model class."""
    visualizer_class = find_visualizer_using_name(visualizer_name)
    return visualizer_class.modify_commandline_options


def create_visualizer(opt):
    visualizer = find_visualizer_using_name(opt.vname)
    instance = visualizer(opt)
    print("visualizer [%s] was created" % type(instance).__name__)
    return instance

