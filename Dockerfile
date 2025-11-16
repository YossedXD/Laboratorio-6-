FROM python:3.11-slim

# Dependencias mínimas para Pygame + pantalla virtual
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libsdl2-gfx-1.0-0 \
    libportmidi0 \
    xvfb \
    x11-utils \
    xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["xvfb-run", "-s", "-screen 0 800x600x24", "python", "juego.py"]
