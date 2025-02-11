# Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).
![workflow](https://github.com/Zuellni/ComfyUI-Custom-Nodes/assets/123005779/692802bb-3d66-4a09-8d90-74e745f8478c)
The workflow above is embedded in the image. You can load it in ComfyUI.
## Installation
Clone the repository to `custom_nodes` in your ComfyUI directory and install the requirements:
```
git clone https://github.com/Zuellni/ComfyUI-Custom-Nodes custom_nodes\Zuellni
pip install -U -r custom_nodes\Zuellni\requirements.txt
```
To update execute the following command in the same directory:
```
git -C custom_nodes\Zuellni pull
```
All required models are downloaded to to the `.cache` directory automatically.
## Aesthetic Nodes
Name | Description
:--- | :---
Aesthetic&nbsp;Loader | Loads models for use with `Aesthetic Filter`.
Aesthetic&nbsp;Filter | Returns `x` best images and a `list` of their indexes based on [cafe_aesthetic](https://huggingface.co/cafeai/cafe_aesthetic)/[cafe_waifu](https://huggingface.co/cafeai/cafe_waifu) scoring. If no models are loaded then acts like `LatentFromBatch` and returns 1 image with 1-based index.
Aesthetic&nbsp;Select | Takes `latents` and a `list` of indexes from `Aesthetic Filter` and returns only the selected `latents`.
## IF Nodes
A poor man's implementation of [DeepFloyd IF](https://huggingface.co/DeepFloyd). Text encoder requires more than 8GB of VRAM. To download the models you will have to agree to the terms of use on the site, create an access token and [log in](https://huggingface.co/docs/huggingface_hub/quick-start#login) with it.
Name | Description
:--- | :---
IF&nbsp;Loader | Loads models for use with other `IF` nodes. `Device` can be used to move the models to specific devices, eg `cuda:0`, `cuda:1`. Leaving it empty enables cpu offloading.
IF&nbsp;Encoder | Encodes prompts for use with `IF Stage I` and `IF Stage II`. Setting `unload` to `True` removes the model from memory. Prompts can be reused without having to reload the encoder.
IF&nbsp;Stage&nbsp;I | Takes the prompt embeds from `IF Encoder` and returns images which can be used with `IF Stage II` or other nodes.
IF&nbsp;Stage&nbsp;II | As above, but also takes `Stage I` or other images and upscales them x4.
IF&nbsp;Stage&nbsp;III | Upscales `Stage II` or other images using [Stable Diffusion x4 upscaler](https://huggingface.co/stabilityai/stable-diffusion-x4-upscaler). Doesn't work with `IF Encoder` embeds, has its own encoder accepting `string` prompts instead. Setting `tile` to `True` allows for upscaling larger images than normally possible.
## Other Nodes
Name | Description
:--- | :---
Latent&nbsp;Decode | Combines `VAEDecode` and `VAEDecodeTiled`. Probably not necessary since `VAEDecodeTiled` is now used on error, but just here for the sake of completeness.
Latent&nbsp;Encode | As above, but adds `batch_size`. Allows loading 1 image and denoising it `x` times without having to create multiple sampler nodes.
Multi&nbsp;Crop | Center crops images/latents to specified dimensions.
Multi&nbsp;Noise | Adds random noise to images/latents.
Multi&nbsp;Repeat | Allows for repeating images/latents `x` times, similar to `Latent Encode`.
Multi&nbsp;Resize | Similar to `LatentUpscale` but uses `scale` instead of width/height. Works with both images and latents.
Load&nbsp;Folder | Loads all images in a specified directory. The images will be cropped/resized if their dimensions aren't equal.
Share&nbsp;Image | Saves images without metadata in a specified directory. Counter resets on restart. Useful for sharing images without having to remove prompts manually.
