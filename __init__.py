from transformers import logging as transformers_logging
from diffusers import logging as diffusers_logging
from warnings import filterwarnings
import logging

from .Nodes import Custom, DeepFloyd


transformers_logging.set_verbosity_error()
diffusers_logging.set_verbosity_error()
logging.getLogger("xformers").addFilter(lambda r: "A matching Triton is not available" not in r.getMessage())
filterwarnings("ignore", category = FutureWarning, message = "The `reduce_labels` parameter is deprecated")
filterwarnings("ignore", category = UserWarning, message = "You seem to be using the pipelines sequentially on GPU")
filterwarnings("ignore", category = UserWarning, message = "TypedStorage is deprecated")


NODE_CLASS_MAPPINGS = {
	# Aesthetic
	"Aesthetic Filter": Custom.Filter,
	"Aesthetic Select": Custom.Select,

	# Image
	"Share Image": Custom.Save,

	# Latent
	"VAE Decode": Custom.Decode,
	"VAE Encode": Custom.Encode,
	"Latent Repeat": Custom.Repeat,

	# Multi
	"Multi Noise": Custom.Noise,
	"Multi Resize": Custom.Resize,

	# DeepFloyd
	"IF Encode": DeepFloyd.Encode,
	"IF Stage I": DeepFloyd.StageI,
	"IF Stage II": DeepFloyd.StageII,
	"IF Stage III": DeepFloyd.StageIII,
}