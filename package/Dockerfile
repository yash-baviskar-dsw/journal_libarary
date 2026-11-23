# Use Ubuntu 22.04 as the base image, matching the reference library pipeline.
FROM ubuntu:22.04

# Install Python and the native build toolchain required for Cython extensions.
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-distutils \
    python3-pip \
    build-essential \
    findutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/journalkit

# Copy only the build inputs and package source into the build image.
COPY ./package/build_Wheel_and_move_wheel.sh .
COPY ./setup.py .
COPY ./README.md .
COPY ./journalkit ./journalkit

# Match the pinned build-tool pattern used by unifyai_library.
RUN pip3 install --upgrade pip setuptools==80.9.0 wheel==0.45.1
RUN pip3 install Cython==0.29.28
RUN pip3 install numpy==1.22.4

# Cython compiles .pyx sources; preserve __init__.py as regular Python.
WORKDIR /app/journalkit/journalkit
RUN find /app/journalkit/journalkit -type f -name "*.py" ! -name "__init__.py" \
    -exec sh -c 'mv "$1" "$(dirname "$1")/$(basename "$1" .py).pyx"' sh {} \;

WORKDIR /app/journalkit
RUN chmod +x /app/journalkit/build_Wheel_and_move_wheel.sh
RUN chmod -R a+rwX /app/journalkit

CMD ["/app/journalkit/build_Wheel_and_move_wheel.sh"]
