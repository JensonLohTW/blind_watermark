#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_SRC = PROJECT_ROOT / "backend"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from app.core.watermark import WaterMark

os.chdir(os.path.dirname(__file__))
bwm = WaterMark(password_wm=1, password_img=1)
# 读取原图
bwm.read_img(filename='pic/ori_img.jpeg')
# 读取水印
bwm.read_wm('pic/watermark.png')
# 打上盲水印
bwm.embed('output/embedded.png')
wm_shape = cv2.imread('pic/watermark.png', flags=cv2.IMREAD_GRAYSCALE).shape

# %% 解水印


bwm1 = WaterMark(password_wm=1, password_img=1)
# 注意需要设定水印的长宽wm_shape
bwm1.extract('output/embedded.png', wm_shape=wm_shape, out_wm_name='output/wm_extracted.png', mode='img')
