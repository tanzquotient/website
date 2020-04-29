# @Copyright    VSETH - Verband der Studierenden an der ETH Zürich
# @Author       Thore Goebel <thgoebel@ethz.ch>
#
# Dockerfile for the tq-website

FROM eu.gcr.io/vseth-public/python36:charlie

# Copy cinit file
COPY cinit.yml /etc/cinit.d/tq-website.yml

# Pillow
#TODO Test which libraries are actually needed
#RUN apt install -y zlib jpeg libxml2-dev libxslt-dev python-dev \
#    build-base jpeg-dev zlib-dev && \
#    LIBRARY_PATH=/lib:/usr/lib pip3 install Pillow==7.1.1

# Install dependencies:
# - git to clone code from Github
# - libpq-dev to build psycopg2 (which in turn is needed for the connection to postgres)
RUN apt install -y git libpq-dev

WORKDIR /app

# Copy the code into the container
COPY . .

# Ensure the scripts are executable
RUN chmod +x pre-start.sh && chmod +x scripts/generate-env.py

# Install requirements
RUN python3 -m pip install -r requirements.txt

# Change permissions on the code so the app-user can access it
RUN chown -R app-user:app-user .

