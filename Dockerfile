FROM localhost:5000/jora/python-web-service:latest
MAINTAINER streamtv85 "streamtv85@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .
ENV DASH_URL_BASE_PATHNAME=/elyamap/
EXPOSE 8050/tcp
CMD ["python", "elyamap/app.py"]