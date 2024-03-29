
"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
import base64
import io
import random
import string
from PIL import Image, ImageFont, ImageDraw

class CaptchaTool(object):
    """
    生成图片验证码
    """

    def __init__(self, width=50, height=12):

        self.width = width
        self.height = height
        # 新图片对象
        self.im = Image.new('RGB', (width, height), 'white')
        # 字体
        self.font = ImageFont.load_default()
        # draw对象
        self.draw = ImageDraw.Draw(self.im)

    def draw_lines(self, num=3):
        """
        划线
        """
        for num in range(num):
            x1 = random.randint(0, self.width / 2)
            y1 = random.randint(0, self.height / 2)
            x2 = random.randint(0, self.width)
            y2 = random.randint(self.height / 2, self.height)
            self.draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    def get_verify_code(self):
        """
        生成验证码图形
        """
        code = ''.join(random.sample(string.digits, 4))
        # 绘制字符串
        for item in range(4):
            self.draw.text((6 + random.randint(-3, 3) + 10 * item, 2 + random.randint(-2, 2)),
                           text=code[item],
                           fill=(random.randint(32, 127),
                                 random.randint(32, 127),
                                 random.randint(32, 127))
                           , font=self.font)
        # 划线
        # self.draw_lines()
        # 高斯模糊
        # im = self.im.filter(ImageFilter.GaussianBlur(radius=1.5))
        self.im = self.im.resize((100, 24))  # 重新设置大小
        buffered = io.BytesIO()
        self.im.save(buffered, format="JPEG")
        img_str = b"data:image/png;base64," + base64.b64encode(buffered.getvalue())
        return img_str.decode('utf-8'), code

