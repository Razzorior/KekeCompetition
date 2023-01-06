import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from torchvision.utils import make_grid

import matplotlib.pyplot as plt


class BaseConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, padding,
                 stride):
        super(BaseConv, self).__init__()

        self.act = nn.ReLU()

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size, padding,
                               stride)

        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size,
                               padding, stride)
        self.conv3 = nn.Conv2d(out_channels, out_channels, kernel_size,
                               padding, stride)
        #self.conv4 = nn.Conv2d(out_channels, out_channels, kernel_size,
                               #padding, stride)
        self.batchnorm1 = nn.BatchNorm2d(out_channels)
        self.batchnorm2 = nn.BatchNorm2d(out_channels)
        self.batchnorm3 = nn.BatchNorm2d(out_channels)
        #self.batchnorm4 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x = self.act(self.batchnorm1(self.conv1(x)))
        x = self.act(self.batchnorm2(self.conv2(x)))
        x = self.act(self.batchnorm3(self.conv3(x)))
        #x = self.act(self.batchnorm4(self.conv4(x)))
        return x


class DownConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, padding,
                 stride):
        super(DownConv, self).__init__()

        self.pool1 = nn.MaxPool2d(kernel_size=2)
        self.conv_block = BaseConv(in_channels, out_channels, kernel_size,
                                   padding, stride)

    def forward(self, x):
        x = self.pool1(x)
        x = self.conv_block(x)
        return x


class UpConv(nn.Module):
    def __init__(self, in_channels, in_channels_skip, out_channels,
                 kernel_size, padding, stride):
        super(UpConv, self).__init__()

        self.conv_trans1 = nn.ConvTranspose2d(
            in_channels, in_channels, kernel_size=2, padding=0, stride=2)
        self.conv_block = BaseConv(
            in_channels=in_channels + in_channels_skip,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride)

    def forward(self, x, x_skip):
        x = self.conv_trans1(x)
        x = torch.cat((x, x_skip), dim=1)
        x = self.conv_block(x)
        return x


class UNet(nn.Module):
    def __init__(self, in_channels, out_channels, n_class, kernel_size,
                 padding, stride):
        super(UNet, self).__init__()

        self.init_conv = BaseConv(in_channels, out_channels, kernel_size,
                                  padding, stride)

        self.down1 = DownConv(out_channels, 2 * out_channels, kernel_size,
                              padding, stride)

        self.down2 = DownConv(2 * out_channels, 4 * out_channels, kernel_size,
                              padding, stride)

        self.down3 = DownConv(4 * out_channels, 8 * out_channels, kernel_size,
                              padding, stride)

        self.down4 = DownConv(8 * out_channels, 16 * out_channels, kernel_size,
                              padding, stride)
        self.down5 = DownConv(16 * out_channels, 32 * out_channels, kernel_size,
                              padding, stride)

        self.up5 = UpConv(32 * out_channels, 16 * out_channels, 16 * out_channels,
                          kernel_size, padding, stride)

        self.up4 = UpConv(16 * out_channels, 8 * out_channels, 8 * out_channels,
                          kernel_size, padding, stride)

        self.up3 = UpConv(8 * out_channels, 4 * out_channels, 4 * out_channels,
                          kernel_size, padding, stride)

        self.up2 = UpConv(4 * out_channels, 2 * out_channels, 2 * out_channels,
                          kernel_size, padding, stride)

        self.up1 = UpConv(2 * out_channels, out_channels, out_channels,
                          kernel_size, padding, stride)

        self.out = nn.Conv2d(out_channels, n_class, kernel_size, padding, stride)

    def forward(self, x):
        # Encoder
        x = self.init_conv(x)
        x1 = self.down1(x)
        x2 = self.down2(x1)
        x3 = self.down3(x2)
        x4 = self.down4(x3)
        x5 = self.down5(x4)
        # Decoder
        x_up = self.up5(x5, x4)
        x_up = self.up4(x_up, x3)
        x_up = self.up3(x_up, x2)
        x_up = self.up2(x_up, x1)
        x_up = self.up1(x_up, x)
        x_out = torch.sigmoid(self.out(x_up))
        return x_out


# Create 10-class segmentation dummy image and target
x = torch.randn(1, 3, 96, 96)
y = torch.empty(1, 10, 96, 96).random_(2)

# model = UNet(in_channels=1,
#             out_channels=64,
#             n_class=10,
#             kernel_size=3,
#             padding=1,
#             stride=1)

# inp = torch.randn(1, 1, 512, 512)
# print(model(inp).shape)
