# FROM continuumio/miniconda3
FROM python:3.6-stretch

# RUN apt-get update -y
# RUN apt-get install build-essential -y

COPY cloud_bot/requirements.txt requirements.txt

# RUN conda create -n py36 python=3.6
# RUN conda run -n py36 pip install -r requirements.txt
RUN pip install -r requirements.txt

ENV TZ=US/Arizona
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY cloud_bot/bot.py /tmp/bot.py

# CMD ["/bin/bash", "-c", "source activate py36 && python -u /tmp/bot.py" ]
CMD ["python", "/tmp/bot.py"]