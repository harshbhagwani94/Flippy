FROM python:3.8-slim-buster
RUN pip3 install pygame
CMD [ "python3", "game.py"]