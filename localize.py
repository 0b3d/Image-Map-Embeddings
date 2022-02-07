from localizer import create_localizer
from models import create_model
from options.localize_options import LocalizeOptions


opt = LocalizeOptions().parse()  # get test options


# Create a model
model = create_model(opt)
model.setup(opt)
model.eval()

# Create a localizer
localizer = create_localizer(opt)
localizer.set_model(model)
localizer.setup()
localizer.localize()


