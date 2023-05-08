# Base image
FROM python:3.11-slim-bullseye

# Load and set locale
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8

# Define working directory
WORKDIR /app

# Copy dependencies file from local host to image
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy directories from local host to image
COPY src ./src
COPY .streamlit/secrets.toml ./.streamlit/secrets.toml

# Expose port
EXPOSE 8501

# Command to lauch streamlit app when container is run
CMD ["streamlit", "run", "src/main.py"]
