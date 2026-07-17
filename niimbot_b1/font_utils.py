from pathlib import Path
import sys

from PIL import ImageFont


def _existing_font(paths):
    for path in paths:
        if path and Path(path).exists():
            return path
    return None


def get_monospace_font_path(bold=False):
    package_dir = Path(__file__).resolve().parent

    if bold:
        bundled_candidates = [
            package_dir / "fonts" / "UbuntuMono-B.ttf",
            package_dir / "fonts" / "DejaVuSansMono-Bold.ttf",
            package_dir / "fonts" / "DejaVuSansMono.ttf",
        ]

        linux_candidates = [
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]

        windows_candidates = [
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/CascadiaMono-Bold.ttf",
            "C:/Windows/Fonts/courbd.ttf",
            "C:/Windows/Fonts/consola.ttf",
        ]
    else:
        bundled_candidates = [
            package_dir / "fonts" / "UbuntuMono-R.ttf",
            package_dir / "fonts" / "DejaVuSansMono.ttf",
        ]

        linux_candidates = [
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]

        windows_candidates = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/CascadiaMono.ttf",
            "C:/Windows/Fonts/cour.ttf",
        ]

    candidates = [str(p) for p in bundled_candidates]

    if sys.platform.startswith("linux"):
        candidates += linux_candidates
    elif sys.platform.startswith("win"):
        candidates += windows_candidates
    else:
        candidates += linux_candidates + windows_candidates

    return _existing_font(candidates)


def load_font(size, bold=False):
    font_path = get_monospace_font_path(bold=bold)

    if font_path:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            pass

    return ImageFont.load_default()
