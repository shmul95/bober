#!/usr/bin/env python3
import torch
import torch.nn as nn
import argparse
import blobconverter
import os

# -----------------------------
# 1. U-Net definition
# -----------------------------
def conv_block(in_c, out_c):
    return nn.Sequential(
        nn.Conv2d(in_c, out_c, 3, padding=1), nn.ReLU(inplace=True),
        nn.Conv2d(out_c, out_c, 3, padding=1), nn.ReLU(inplace=True),
    )

class UNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc1 = conv_block(3, 64);   self.pool1 = nn.MaxPool2d(2)
        self.enc2 = conv_block(64,128);  self.pool2 = nn.MaxPool2d(2)
        self.enc3 = conv_block(128,256); self.pool3 = nn.MaxPool2d(2)
        self.enc4 = conv_block(256,512); self.pool4 = nn.MaxPool2d(2)
        self.bottleneck = conv_block(512,1024)
        self.up4 = nn.ConvTranspose2d(1024,512,2,2); self.dec4 = conv_block(1024,512)
        self.up3 = nn.ConvTranspose2d(512,256,2,2);  self.dec3 = conv_block(512,256)
        self.up2 = nn.ConvTranspose2d(256,128,2,2);  self.dec2 = conv_block(256,128)
        self.up1 = nn.ConvTranspose2d(128, 64,2,2);  self.dec1 = conv_block(128, 64)
        self.conv_last = nn.Conv2d(64,1,1)

    def forward(self, x):
        s1 = self.enc1(x); p1 = self.pool1(s1)
        s2 = self.enc2(p1); p2 = self.pool2(s2)
        s3 = self.enc3(p2); p3 = self.pool3(s3)
        s4 = self.enc4(p3); p4 = self.pool4(s4)
        b  = self.bottleneck(p4)
        d4 = self.dec4(torch.cat([self.up4(b), s4], 1))
        d3 = self.dec3(torch.cat([self.up3(d4), s3], 1))
        d2 = self.dec2(torch.cat([self.up2(d3), s2], 1))
        d1 = self.dec1(torch.cat([self.up1(d2), s1], 1))
        return self.conv_last(d1)

# -----------------------------
# 2. Script entry point
# -----------------------------
def main(pth_path, onnx_name="unet.onnx", blob_name="unet.blob", input_shape=(1, 3, 192, 320)):
    print(f"Loading PyTorch model from: {pth_path}")
    model = UNet()
    model.load_state_dict(torch.load(pth_path, map_location="cpu"))
    model.eval()

    dummy_input = torch.randn(input_shape)
    print("Exporting to ONNX...")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_name,
        input_names=["input"],
        output_names=["output"],
        opset_version=11
    )

    print(f"Converting to .blob via blobconverter...")
    blob_path = blobconverter.from_onnx(
        onnx_name,             # the model path is now the first required arg
        shaves=6,
        output_dir=os.path.dirname(os.path.abspath(blob_name)),
    )

    print(f"✅ Blob saved to: {blob_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PyTorch .pth model to OAK-D .blob")
    parser.add_argument("pth_path", type=str, help="Path to .pth PyTorch model")
    args = parser.parse_args()

    main(args.pth_path)
