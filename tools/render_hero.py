#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成首页 3D 渲染配图（真三维光照的凹版雕刻橙子，透明背景）。

一次性脚本，依赖 numpy + Pillow（不在 requirements.txt 里，产物已提交到仓库）：
    python tools/render_hero.py
输出：theme/hero.png 与 theme/hero.webp（取体量小者用于站点）
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "theme"
S = 900  # 输出边长

# ── 场景 ────────────────────────────────────────────────────────────────
CX, CY, R = 450.0, 470.0, 268.0          # 球体（果身）
SHADOW_Y = 792.0                          # 地面接触阴影中心


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def normalize(v):
    n = np.sqrt((v ** 2).sum(axis=0)) + 1e-9
    return v / n


yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)

# ── 接触阴影（椭圆软阴影，画在最底层）────────────────────────────────────
sdx = (xx - CX) / (R * 1.10)
sdy = (yy - SHADOW_Y) / (R * 0.20)
sdist = np.sqrt(sdx ** 2 + sdy ** 2)
shadow = smoothstep(1.0, 0.10, sdist) ** 1.35

# ── 球体解析求交 ────────────────────────────────────────────────────────
px = (xx - CX) / R
py = (yy - CY) / R
d2 = px ** 2 + py ** 2
inside = d2 < 1.0
nz = np.sqrt(np.clip(1.0 - d2, 0, 1))
n = np.stack([px, -py, nz], axis=0)          # z 轴朝向观察者
n = normalize(n)

edge = np.sqrt(np.clip(d2, 0, None))          # 到轮廓的归一化距离
cov = smoothstep(1.0, 1.0 - 1.6 / R, 1.0 - (edge - 0.0) + 0.0)  # 抗锯齿用
cov = smoothstep(1.0 + 1.5 / R, 1.0 - 1.5 / R, edge)

# ── 凹版雕刻纹理：经纬线刻痕 ────────────────────────────────────────────
lat = np.arcsin(np.clip(n[1], -1, 1))
lon = np.arctan2(n[0], np.maximum(n[2], 1e-4))
groove = (np.sin(lat * 17.0) * np.sin(lon * 15.0))
groove_s = np.sin(lat * 17.0)
fine = np.sin((lat * 17.0 + lon * 15.0) * 0.5)
engrave = 0.5 + 0.5 * groove
fine_line = 0.5 + 0.5 * fine

# 刻痕法线扰动（屏幕空间近似，让刻线有体积）
bump = groove * 0.10
n_b = normalize(np.stack([n[0] + bump * np.cos(lon), n[1] + bump * np.cos(lat), n[2]], axis=0))

# ── 材质：暖橙渐变 ──────────────────────────────────────────────────────
base_lo = np.array([0.62, 0.19, 0.02], dtype=np.float32)   # 底部深
base_hi = np.array([1.00, 0.68, 0.30], dtype=np.float32)   # 顶部亮
mix = np.clip(0.5 + 0.5 * n_b[1], 0, 1) ** 0.85
albedo = base_lo[:, None, None] * (1 - mix) + base_hi[:, None, None] * mix
albedo *= (0.80 + 0.20 * engrave)[None, :, :]              # 刻痕变暗
albedo *= (0.94 + 0.06 * fine_line)[None, :, :]

# ── 光照：主光 + 补光 + 环境 + 轮廓光 ───────────────────────────────────
KEY = normalize(np.array([-0.45, 0.72, 0.72], dtype=np.float32))   # 左上主光
FILL = normalize(np.array([0.78, -0.10, 0.55], dtype=np.float32))  # 右侧补光
sky = np.stack([np.full_like(n[0], 0.0), n[1], n[2]], axis=0)      # 天光方向（近似）

ndl = np.clip((n_b * KEY[:, None, None]).sum(axis=0), 0, 1)
ndf = np.clip((n_b * FILL[:, None, None]).sum(axis=0), 0, 1)
amb = 0.30 + 0.24 * np.clip(n_b[1], 0, 1) + 0.08 * np.clip(n_b[2], 0, 1)

light = (0.95 * ndl + 0.22 * ndf + amb)
# 底部自遮挡
light *= (0.72 + 0.28 * smoothstep(-0.85, -0.10, n_b[1]))

# 高光（Blinn-Phong + 菲涅尔轮廓光）
V = np.stack([np.zeros_like(n[0]), np.zeros_like(n[1]), np.ones_like(n[2])], axis=0)
H = normalize(KEY[:, None, None] + V)
spec = np.clip((n_b * H).sum(axis=0), 0, 1) ** 90.0
spec_color = np.array([1.0, 0.94, 0.86], dtype=np.float32)
fres = (1.0 - np.clip(n_b[2], 0, 1)) ** 3.2

rgb = albedo * light[None, :, :]
rgb += spec_color[:, None, None] * (spec * 0.95)[None, :, :]
rgb += np.array([1.0, 0.55, 0.25], dtype=np.float32)[:, None, None] * (fres * 0.30 * np.clip(KEY[0] * -1 + 0.6, 0, 1))[None, :, :]

# 与阴影合成（刻线不覆盖阴影）
alpha = np.clip(cov, 0, 1)
shadow_rgb = np.array([0.05, 0.03, 0.02], dtype=np.float32)[:, None, None]
sh = shadow * 0.42

# 地面阴影先铺，再叠果身
out = np.zeros((3, S, S), dtype=np.float32)
a = np.zeros((S, S), dtype=np.float32)
out += shadow_rgb * sh[None, :, :]
a += sh * 0.6
m = alpha[None, :, :]
out = out * (1 - m) + rgb * m
a = a * (1 - alpha) + alpha

# ── 叶子（两片，解析着色）───────────────────────────────────────────────
def leaf(cx, cy, rx, ry, ang, tone=1.0):
    ca, sa = np.cos(ang), np.sin(ang)
    lx = (xx - cx) * ca + (yy - cy) * sa
    ly = -(xx - cx) * sa + (yy - cy) * ca
    u = lx / rx
    v = ly / ry
    # 叶片形状：|v| <= (1-|u|)^1.35
    shape = 1.0 - np.abs(u)
    inside_l = (np.abs(v) <= np.clip(shape, 0, 1) ** 1.35) & (np.abs(u) <= 1.0)
    cov_l = smoothstep(0.0, 1.0, (np.clip(shape, 0, 1) ** 1.35 - np.abs(v)) * ry / 1.6)
    # 伪法线：由形状场梯度近似
    thick = np.sqrt(np.clip(1.0 - (np.abs(v) / np.clip(shape, 1e-3, 1) ** 1.35) ** 2, 0, 1))
    nlx = -np.clip(u, -1, 1) * 0.55
    nly = np.clip(v, -1, 1) * 0.35
    nlz = np.sqrt(np.clip(1.0 - nlx ** 2 - nly ** 2, 0, 1))
    nl = normalize(np.stack([nlx, nly, nlz], axis=0).astype(np.float32))
    lit = 0.42 + 0.72 * np.clip((nl * KEY[:, None, None]).sum(axis=0), 0, 1)
    g_lo = np.array([0.16, 0.34, 0.20], dtype=np.float32) * tone
    g_hi = np.array([0.45, 0.72, 0.42], dtype=np.float32) * tone
    g = g_lo[:, None, None] * (1 - thick) + g_hi[:, None, None] * thick
    rgb_l = g * lit[None, :, :]
    vein = np.exp(-((np.abs(v) * ry) ** 2) / (2 * 3.2 ** 2))
    rgb_l += np.array([0.20, 0.30, 0.18], dtype=np.float32)[:, None, None] * (vein * 0.35)[None, :, :]
    spec_l = np.clip((nl * normalize(KEY + np.array([0, 0, 1], dtype=np.float32))[:, None, None]).sum(axis=0), 0, 1) ** 40
    rgb_l += np.array([0.9, 1.0, 0.9], dtype=np.float32)[:, None, None] * (spec_l * 0.25)[None, :, :]
    return rgb_l, np.clip(cov_l, 0, 1) * inside_l.astype(np.float32) * 0 + np.clip(cov_l, 0, 1)

# 右叶（大）、左叶（小）
for (cx, cy, rx, ry, ang, tone) in [(560, 262, 168, 74, -0.42, 1.0), (352, 286, 138, 60, 0.30, 0.9)]:
    rgb_l, a_l = leaf(cx, cy, rx, ry, ang, tone)
    m = np.clip(a_l, 0, 1)[None, :, :]
    out = out * (1 - m) + rgb_l * m
    a = a * (1 - np.clip(a_l, 0, 1)) + np.clip(a_l, 0, 1)

# 果梗
stem = (((xx - 452) / 13.0) ** 2 + ((yy - 236) / 78.0) ** 2) < 1.0
stem_cov = smoothstep(1.0, 0.72, np.sqrt(((xx - 452) / 13.0) ** 2 + ((yy - 236) / 78.0) ** 2))
stem_rgb = np.array([0.30, 0.20, 0.10], dtype=np.float32)[:, None, None] * (0.7 + 0.6 * np.clip((xx - 430) / 44.0, 0, 1))[None, :, :]
m = stem_cov[None, :, :]
out = out * (1 - m) + stem_rgb * m
a = a * (1 - stem_cov) + stem_cov

# ── 输出 ────────────────────────────────────────────────────────────────
rgb8 = np.clip(out ** (1 / 1.9), 0, 1) * 255.0     # 轻微 gamma，压缩高光
arr = np.concatenate([rgb8, (np.clip(a, 0, 1) * 255.0)[None, :, :]], axis=0)
img = Image.fromarray(np.transpose(arr, (1, 2, 0)).astype(np.uint8), "RGBA")
img = img.filter(ImageFilter.GaussianBlur(0.4))

OUT.mkdir(exist_ok=True)
png = OUT / "hero.png"
img.save(png, "PNG", optimize=True)
sizes = {"hero.png": png.stat().st_size}
try:
    webp = OUT / "hero.webp"
    img.save(webp, "WEBP", quality=88, method=6)
    sizes["hero.webp"] = webp.stat().st_size
except Exception as exc:  # noqa: BLE001
    print("webp 保存失败:", exc, file=sys.stderr)

for k, v in sizes.items():
    print(f"  {k}: {v/1024:.0f} KB")
print(f"渲染完成 -> {OUT}")
