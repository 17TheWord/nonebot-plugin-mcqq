import io
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont  # type: ignore

from ..config import plugin_config

MC_COLORS = {
    "0": (0, 0, 0),  # &0 - 黑色
    "1": (0, 0, 170),  # &1 - 深蓝色
    "2": (0, 170, 0),  # &2 - 深绿色
    "3": (0, 170, 170),  # &3 - 深青色
    "4": (170, 0, 0),  # &4 - 深红色
    "5": (170, 0, 170),  # &5 - 紫色
    "6": (255, 170, 0),  # &6 - 金色
    "7": (170, 170, 170),  # &7 - 灰色
    "8": (85, 85, 85),  # &8 - 深灰色
    "9": (85, 85, 255),  # &9 - 蓝色
    "a": (85, 255, 85),  # &a - 绿色
    "b": (85, 255, 255),  # &b - 青色
    "c": (255, 85, 85),  # &c - 红色
    "d": (255, 85, 255),  # &d - 粉色
    "e": (255, 255, 85),  # &e - 黄色
    "f": (255, 255, 255),  # &f - 白色
}


class ColoredTextSegment:
    def __init__(self, text: str, color: tuple = (255, 255, 255)):
        self.text = text
        self.color = color

    def __str__(self):
        return self.text

    def get_color(self):
        return self.color


# 解析Minecraft颜色代码
def parse_mc_colors(text) -> list[ColoredTextSegment]:
    # 支持 & 和 § 作为颜色代码前缀
    parts = re.split(r"([&§][0-9a-fk-or])", text)
    segments = []
    current_color = (255, 255, 255)  # 默认白色

    for part in parts:
        if part and (part.startswith("&") or part.startswith("§")) and len(part) == 2:
            # 更新当前颜色
            current_color = MC_COLORS.get(part[1], (255, 255, 255))
        elif part:
            # 将文本片段与当前颜色关联
            segments.append(ColoredTextSegment(part, current_color))

    return segments


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text_segments: list[ColoredTextSegment],
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[list[ColoredTextSegment]]:
    lines = []
    current_line = []
    current_width = 0

    for segment in text_segments:
        split_text = segment.text.split("\n")
        for part in split_text:
            segment_width = draw.textlength(part, font=font)
            if current_width + segment_width > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = [ColoredTextSegment(part, segment.get_color())]
                current_width = segment_width
            else:
                current_line.append(ColoredTextSegment(part, segment.get_color()))
                current_width += segment_width
            if len(split_text) > 1:
                lines.append(current_line)
                current_line = []
                current_width = 0
    if current_line:
        lines.append(current_line)
    return lines


# 绘制带颜色的文字
def draw_result_image(text: str) -> bytes:
    image = Image.open(Path(__file__).parent.parent / "resource" / "bg.png")
    draw = ImageDraw.Draw(image)
    font_size = 15
    padding = 10

    font = ImageFont.truetype(plugin_config.ttf_path, font_size)

    # 解析带颜色的文本
    segments = parse_mc_colors(text)

    # 自动换行处理
    max_width = image.width - 2 * padding  # 考虑内边距
    lines = wrap_text(draw, segments, font, max_width)

    # 绘制文本
    x = padding
    y = padding
    line_height = font_size + 2
    for line in lines:
        current_x = x
        for segment in line:
            draw.text((current_x, y), segment.text, font=font, fill=segment.get_color())
            current_x += draw.textlength(segment.text, font=font)
        y += line_height

    return image_to_bytes(image)


def image_to_bytes(image: Image.Image) -> bytes:
    img_byte = io.BytesIO()
    image.save(img_byte, format="PNG")
    return img_byte.getvalue()
