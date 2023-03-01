FROM python:3.12.0a5-slim
RUN pip3 install pygame
CMD [ "python3", "game.py"]