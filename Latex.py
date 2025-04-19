import warnings
import sys
import os
import pyperclip
from contextlib import contextmanager
from PIL import ImageGrab, ImageOps, ImageEnhance
from pix2tex.cli import LatexOCR

# 屏蔽所有 Python warnings
warnings.filterwarnings('ignore')

# 创建一个 context manager，临时屏蔽 stderr
@contextmanager
def suppress_stderr():
    stderr_fileno = sys.stderr.fileno()

    def _redirect_stderr(to_fd):
        sys.stderr.close()
        os.dup2(to_fd, stderr_fileno)
        sys.stderr = os.fdopen(stderr_fileno, 'w')

    with os.fdopen(os.dup(stderr_fileno), 'w') as old_stderr:
        with open(os.devnull, 'w') as devnull:
            _redirect_stderr(devnull.fileno())
        try:
            yield
        finally:
            _redirect_stderr(old_stderr.fileno())

# 读取剪贴板图片
with suppress_stderr():
    img = ImageGrab.grabclipboard()

if img is None:
    print("❌ 剪贴板里没有图片！请先复制一张图片。")
else:
    # 转灰度图
    gray_img = img.convert('L')
    mean_brightness = gray_img.getextrema()
    avg_brightness = (mean_brightness[0] + mean_brightness[1]) / 2

    if avg_brightness < 128:
        print("检测到黑底白字，正在反色处理...")
        inverted_img = ImageOps.invert(gray_img)

        # 加强对比度，让反色后的字更黑
        enhancer = ImageEnhance.Contrast(inverted_img)
        enhanced_img = enhancer.enhance(2.0)  # 对比度乘以2倍，可根据需要调整
        img = enhanced_img.convert('RGB')
    else:
        img = img.convert('RGB')

    model = LatexOCR()
    latex_code = model(img)
    print("✅ 识别出的LaTeX公式是：\n", latex_code)

    # 自动复制到剪贴板
    pyperclip.copy(latex_code)
    print("✅ LaTeX代码已自动复制到剪贴板！现在可以直接粘贴啦～")
