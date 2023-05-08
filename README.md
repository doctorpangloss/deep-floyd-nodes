# Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

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
All required models are currently downloaded to the huggingface `.cache` directory.
## List
### Custom Nodes
A bunch of custom/modded nodes. Most work with both batched images and latents.
#### Aesthetic Loader
Loads models for use with `Aesthetic Filter`.
#### Aesthetic Filter
Returns `x` best images and a `list` of their indexes based on [cafe_aesthetic](https://huggingface.co/cafeai/cafe_aesthetic)/[cafe_waifu](https://huggingface.co/cafeai/cafe_waifu) scoring. If no models are loaded then acts like `LatentFromBatch` and returns 1 image with 1-based index.
#### Aesthetic Select
Takes `latents` and a `list` of indexes from `Aesthetic Filter` and returns only the selected `latents`.
#### Share Image
Saves images without metadata in specified directory. Counter resets on restart. Useful for sharing images without having to remove prompts manually.
#### VAE Decoder
Combines `VAEDecode` and `VAEDecodeTiled`. Probably not necessary since `VAEDecodeTiled` is now used on error but just here for the sake of completeness.
#### VAE Encoder
As above, but adds `batch_size`. Allows for loading 1 image and denoising it `x` times without having to create multiple `KSampler` nodes.
#### Multi Noise
Adds random black and white/color noise to images/latents.
#### Multi Repeat
Allows for repeating images/latents `x` times, similar to `VAE Encoder`.
#### Multi Resize
Similar to `LatentUpscale` but takes `scale` instead of width/height. Works with both images and latents.
### DeepFloyd Nodes
A poor man's implementation of [DeepFloyd IF](https://huggingface.co/docs/diffusers/api/pipelines/if). All the stages with text encoder unloading enabled currently <ins>require more than 8GB of VRAM</ins>.
#### IF Loader
Loads models for use with other `IF` nodes.
#### IF Encoder
Encodes positive/negative prompts for use with `IF Stage I` and `IF Stage II`. Setting `unload` to `True` removes the model from memory after it's finished. Prompts can be reused without having to reload it.
#### IF Stage I
Takes the prompt embeds from `IF Encoder` and returns `64x64px` images which can be used with `IF Stage II` or other nodes.
#### IF Stage II
As above, but also takes `Stage I` or other images. Returns `256x256px` images which can be used with `IF Stage III` or other nodes such as upscalers or samplers. Images larger than `64x64px` will still result in `256x256px` output.
#### IF Stage III
Upscales `Stage II` or other images `4 times`, resulting in `1024x1024px` images for `Stage II`. Doesn't work with `IF Encoder` embeds, has its own encoder accepting `string` prompts instead. Setting `tile` to `True` additionally allows for upscaling larger images than normally possible, around `768x768px` base with 12GB of VRAM.
