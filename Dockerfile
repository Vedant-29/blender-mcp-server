# Force x86_64 since Blender only provides Linux x86_64 binaries
FROM --platform=linux/amd64 python:3.11-slim-bookworm

# Install Blender dependencies (bookworm-compatible packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    libxi6 \
    libxrender1 \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libegl-mesa0 \
    libxkbcommon0 \
    libsm6 \
    libice6 \
    libxxf86vm1 \
    libxfixes3 \
    libxext6 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender 3.6 LTS headless (x86_64)
RUN wget -q https://mirror.clarkson.edu/blender/release/Blender3.6/blender-3.6.16-linux-x64.tar.xz \
    && tar -xf blender-3.6.16-linux-x64.tar.xz \
    && mv blender-3.6.16-linux-x64 /opt/blender \
    && rm blender-3.6.16-linux-x64.tar.xz

ENV PATH="/opt/blender:${PATH}"
ENV BLENDER_PATH="/opt/blender"

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Create storage directories
RUN mkdir -p /app/scenes /app/output

EXPOSE 8080

CMD ["python", "-m", "src.server"]
