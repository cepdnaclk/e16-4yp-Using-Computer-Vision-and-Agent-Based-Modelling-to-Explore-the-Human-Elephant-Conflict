#!/bin/bash

echo "Downloading the pretrained models..."
wget -nc https://github.com/SwinTransformer/storage/releases/download/v1.0.8/swin_tiny_patch4_window7_224_22k.pth

wget -nc https://github.com/SwinTransformer/storage/releases/download/v1.0.3/moby_swin_t_300ep_pretrained.pth

echo "Converted model parameters..."
python tools/model_converters/swin2mmseg.py swin_tiny_patch4_window7_224_22k.pth swin_tiny_patch4_window7_224_22k_converted.pth