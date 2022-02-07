from visualizations.base_options import BaseOptions
from visualizations import create_visualizer

if __name__ == '__main__':

    opt = BaseOptions().parse()
    visualizer = create_visualizer(opt)
    visualizer.print_info()
    visualizer.show()
