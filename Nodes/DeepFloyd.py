from comfy.model_management import throw_exception_if_processing_interrupted, xformers_enabled
from comfy.utils import ProgressBar

from transformers import T5EncoderModel
from diffusers import DiffusionPipeline
import torch
import gc


class Loader:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"model": (["M", "L", "XL"], {"default": "M"}),
				"stage": (["I", "II", "III"], {"default": "I"}),
			},
		}

	CATEGORY = "Zuellni/DeepFloyd"
	FUNCTION = "process"
	RETURN_TYPES = ("PIPE",)

	def process(self, model, stage):
		pipe = None

		if stage == "III":
			pipe = DiffusionPipeline.from_pretrained(
				"stabilityai/stable-diffusion-x4-upscaler",
				torch_dtype = torch.float16,
				requires_safety_checker = False,
				feature_extractor = None,
				safety_checker = None,
				watermarker = None,
			)
		else:
			pipe = DiffusionPipeline.from_pretrained(
				f"DeepFloyd/IF-{stage}-{model}-v1.0",
				variant = "fp16",
				torch_dtype = torch.float16,
				requires_safety_checker = False,
				feature_extractor = None,
				safety_checker = None,
				text_encoder = None,
				watermarker = None,
			)

		pipe.unet.to(torch.float16, memory_format = torch.channels_last)
		pipe.enable_model_cpu_offload()

		if xformers_enabled():
			pipe.enable_xformers_memory_efficient_attention()

		return (pipe,)


class Encoder:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"unload": ([False, True], {"default": False}),
				"positive": ("STRING", {"default": "", "multiline": True}),
				"negative": ("STRING", {"default": "", "multiline": True}),
			},
		}

	CATEGORY = "Zuellni/DeepFloyd"
	FUNCTION = "process"
	RETURN_TYPES = ("POSITIVE", "NEGATIVE",)

	def process(self, unload, positive, negative):
		text_encoder = T5EncoderModel.from_pretrained(
			f"DeepFloyd/IF-I-M-v1.0",
			subfolder = "text_encoder",
			variant = "fp16",
			torch_dtype = torch.float16,
			load_in_8bit = True,
			device_map = "auto",
		)

		pipe = DiffusionPipeline.from_pretrained(
			f"DeepFloyd/IF-I-M-v1.0",
			text_encoder = text_encoder,
			requires_safety_checker = False,
			feature_extractor = None,
			safety_checker = None,
			unet = None,
			watermarker = None,
		)

		if xformers_enabled():
			pipe.enable_xformers_memory_efficient_attention()

		positive, negative = pipe.encode_prompt(
			prompt = positive,
			negative_prompt = negative,
		)

		if unload:
			del pipe, text_encoder
			gc.collect()

		return (positive, negative,)


class StageI:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"pipe": ("PIPE",),
				"positive": ("POSITIVE",),
				"negative": ("NEGATIVE",),
				"batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
				"steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
				"cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
			},
		}

	CATEGORY = "Zuellni/DeepFloyd"
	FUNCTION = "process"
	RETURN_TYPES = ("IMAGE",)

	def process(self, pipe, positive, negative, batch_size, seed, steps, cfg):
		progress = ProgressBar(steps)

		def callback(step, time_step, latents):
			throw_exception_if_processing_interrupted()
			progress.update_absolute(step)

		image = pipe(
			prompt_embeds = positive,
			negative_prompt_embeds = negative,
			generator = torch.manual_seed(seed),
			guidance_scale = cfg,
			num_images_per_prompt = batch_size,
			num_inference_steps = steps,
			callback = callback,
			output_type = "pt",
		).images

		image = (image / 2 + 0.5).clamp(0, 1)
		image = image.cpu().permute(0, 2, 3, 1).float()
		return (image,)


class StageII:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"pipe": ("PIPE",),
				"image": ("IMAGE",),
				"positive": ("POSITIVE",),
				"negative": ("NEGATIVE",),
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
				"steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
				"cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
			},
		}

	CATEGORY = "Zuellni/DeepFloyd"
	FUNCTION = "process"
	RETURN_TYPES = ("IMAGE",)

	def process(self, pipe, image, positive, negative, seed, steps, cfg):
		image = image.permute(0, 3, 1, 2)
		progress = ProgressBar(steps)
		batch_size = image.shape[0]

		if batch_size > 1:
			positive = positive.repeat(batch_size, 1, 1)
			negative = negative.repeat(batch_size, 1, 1)

		def callback(step, time_step, latents):
			throw_exception_if_processing_interrupted()
			progress.update_absolute(step)

		image = pipe(
			image = image,
			prompt_embeds = positive,
			negative_prompt_embeds = negative,
			generator = torch.manual_seed(seed),
			guidance_scale = cfg,
			num_inference_steps = steps,
			callback = callback,
			output_type = "pt",
		).images.cpu().permute(0, 2, 3, 1).float()

		return (image,)


class StageIII:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"pipe": ("PIPE",),
				"image": ("IMAGE",),
				"tile": ([False, True], {"default": False}),
				"noise": ("INT", {"default": 100, "min": 0, "max": 100}),
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
				"steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
				"cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
				"positive": ("STRING", {"default": "", "multiline": True}),
				"negative": ("STRING", {"default": "", "multiline": True}),
			},
		}

	CATEGORY = "Zuellni/DeepFloyd"
	FUNCTION = "process"
	RETURN_TYPES = ("IMAGE",)

	def process(self, pipe, image, tile, noise, seed, steps, cfg, positive, negative):
		image = image.permute(0, 3, 1, 2)
		progress = ProgressBar(steps)
		batch_size = image.shape[0]

		if batch_size > 1:
			positive = [positive] * batch_size
			negative = [negative] * batch_size

		def callback(step, time_step, latents):
			throw_exception_if_processing_interrupted()
			progress.update_absolute(step)

		if tile:
			pipe.vae.enable_tiling()

		image = pipe(
			image = image,
			prompt = positive,
			negative_prompt = negative,
			noise_level = noise,
			generator = torch.manual_seed(seed),
			guidance_scale = cfg,
			num_inference_steps = steps,
			callback = callback,
			output_type = "pt",
		).images.cpu().permute(0, 2, 3, 1).float()

		return (image,)