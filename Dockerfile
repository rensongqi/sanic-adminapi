FROM python:3.10.5-slim-buster

ENV TZ=Asia/Shanghai

WORKDIR /data

ADD . .

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

EXPOSE 8011
CMD ["python3", "/data/main.py"]