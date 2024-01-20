FROM nikolaik/python-nodejs:python3.12-nodejs18

ENV CDK_VERSION=2.122.0

WORKDIR /workspace/

RUN apt-get update && apt-get install -y curl unzip less

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && ./aws/install

RUN npm install -g aws-cdk@${CDK_VERSION}

COPY ./pyproject.toml ./

RUN pip install poetry && poetry config virtualenvs.create false && poetry install
