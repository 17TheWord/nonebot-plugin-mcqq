import importlib
import sys
import types

import pytest


@pytest.fixture
def draw_result_module(app, monkeypatch):
    class FakeImage:
        width = 160

        def save(self, buffer, format):
            assert format == "PNG"
            buffer.write(b"fake-png-bytes")

    class FakeImageModule:
        Image = FakeImage

        @staticmethod
        def open(_path):
            return FakeImage()

    class FakeDraw:
        def __init__(self, _image):
            self.drawn_text = []

        def textlength(self, text, font):
            return len(text) * 10

        def text(self, xy, text, font, fill):
            self.drawn_text.append((xy, text, fill))

    class FakeImageDrawModule:
        ImageDraw = FakeDraw

        @staticmethod
        def Draw(image):
            return FakeDraw(image)

    class FakeImageFontModule:
        FreeTypeFont = object

        @staticmethod
        def truetype(_path, _font_size):
            return object()

    fake_pil = types.ModuleType("PIL")
    fake_image_module = FakeImageModule()
    fake_image_draw_module = FakeImageDrawModule()
    fake_image_font_module = FakeImageFontModule()
    monkeypatch.setitem(sys.modules, "PIL", fake_pil)
    monkeypatch.setitem(sys.modules, "PIL.Image", fake_image_module)
    monkeypatch.setitem(sys.modules, "PIL.ImageDraw", fake_image_draw_module)
    monkeypatch.setitem(sys.modules, "PIL.ImageFont", fake_image_font_module)
    sys.modules.pop("nonebot_plugin_mcqq.utils.draw_result", None)

    module = importlib.import_module("nonebot_plugin_mcqq.utils.draw_result")
    yield module
    sys.modules.pop("nonebot_plugin_mcqq.utils.draw_result", None)


def test_parse_mc_colors_supports_ampersand_and_section_codes(draw_result_module):
    segments = draw_result_module.parse_mc_colors("plain &atest §cerror &xdefault")

    assert [str(segment) for segment in segments] == [
        "plain ",
        "test ",
        "error &xdefault",
    ]
    assert segments[0].get_color() == (255, 255, 255)
    assert segments[1].get_color() == (85, 255, 85)
    assert segments[2].get_color() == (255, 85, 85)


def test_wrap_text_splits_long_and_newline_segments(draw_result_module):
    draw = sys.modules["PIL.ImageDraw"].Draw(None)
    font = object()

    lines = draw_result_module.wrap_text(
        draw=draw,
        text_segments=[
            draw_result_module.ColoredTextSegment("short", (255, 255, 255)),
            draw_result_module.ColoredTextSegment("\nnext", (85, 255, 85)),
            draw_result_module.ColoredTextSegment("very-long-text", (255, 85, 85)),
        ],
        font=font,
        max_width=40,
    )

    assert len(lines) >= 3
    assert "".join(str(segment) for line in lines for segment in line)


def test_image_to_bytes_returns_bytes(draw_result_module):
    image = sys.modules["PIL.Image"].Image()

    result = draw_result_module.image_to_bytes(image)

    assert result == b"fake-png-bytes"


def test_draw_result_image_returns_bytes(draw_result_module):
    result = draw_result_module.draw_result_image("&aSuccess\n§cFailed")

    assert result == b"fake-png-bytes"
