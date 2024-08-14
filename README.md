Here's a comprehensive GitHub README for your AWS RAG application, including the new steps for Docker and CI/CD:

---

# AWS RAG Application

## Overview

This application, developed using Python and Streamlit, leverages AI models from AWS Bedrock to process PDF uploads and store their embeddings in a Faiss database. The vector embeddings are stored in AWS S3, enabling easy retrieval and analysis of user interactions and feedback. The application is containerized using Docker, deployed on an EC2 instance for computing power, and utilizes GitHub Actions for CI/CD.

## Features

- **PDF Processing**: Upload PDFs and extract embeddings using AI models from AWS Bedrock.
- **Embedding Storage**: Store vector embeddings in AWS S3 for efficient retrieval and analysis.
- **Streamlit Interface**: A user-friendly web interface for interacting with the application.
- **Dockerized Deployment**: Containerized application for easy deployment and scaling.
- **CI/CD with GitHub Actions**: Automated build, test, and deployment pipeline.

## Prerequisites

- AWS Account
- EC2 Instance
- Docker
- AWS CLI
- GitHub Actions

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/aws-rag-application.git
cd aws-rag-application
```

### 2. Dockerize the Application

Build the Docker image:

```bash
docker build -t your-dockerhub-username/aws-rag-application .
```

Push the Docker image to Docker Hub:

```bash
docker push your-dockerhub-username/aws-rag-application
```

### 3. Setup EC2 Instance

#### Move the Key Pair File

```bash
mv ~/Downloads/your-key-pair.pem ~/.ssh/
chmod 400 ~/.ssh/your-key-pair.pem
```

#### Connect to EC2 Instance

```bash
ssh -i ~/.ssh/your-key-pair.pem ec2-user@your-ec2-public-dns
```

#### Update System Packages

```bash
sudo yum update -y
```

#### Install Docker

```bash
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```

Log out and log back in for the group changes to take effect.

#### Ensure Docker is Running

If Docker is installed but not running, start it:

```bash
sudo systemctl start docker
```

Enable Docker to start on boot:

```bash
sudo systemctl enable docker
```

Check Docker socket permissions:

```bash
ls -l /var/run/docker.sock
```

Ensure the Docker socket is accessible and owned by the docker group. Add `ec2-user` to the docker group:

```bash
sudo usermod -aG docker ec2-user
```

### 4. Deploy Docker Container on EC2

Pull the Docker image from Docker Hub:

```bash
docker pull your-dockerhub-username/aws-rag-application
```

Run the Docker container:

```bash
docker run -d -p 8501:8501 your-dockerhub-username/aws-rag-application
```

### 5. Configure CI/CD with GitHub Actions
Refer to the actual yml file this is just a 
Create a `.github/workflows/docker-image.yml` file in your repository with the following content:

```yaml
name: Docker Image CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1

    - name: Cache Docker layers
      uses: actions/cache@v2
      with:
        path: /tmp/.buildx-cache
        key: ${{ runner.os }}-buildx-${{ github.sha }}
        restore-keys: |
          ${{ runner.os }}-buildx-

    - name: Log in to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v2
      with:
        push: true
        tags: your-dockerhub-username/aws-rag-application:latest
```

Replace `your-dockerhub-username` with your actual Docker Hub username. Make sure to add your Docker Hub credentials as secrets in your GitHub repository settings.

### 6. Verify Deployment

Open your browser and navigate to `http://your-ec2-public-dns:8501'[your-ec2-public-dns is your IPv4 Public DNS] to access the Streamlit application.

## Usage

Upload PDF files through the Streamlit interface. The application will process the files using AI models from AWS Bedrock, store the embeddings in AWS S3, and allow you to analyze and retrieve the embeddings.

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.

---

Feel free to customize the README as per your specific requirements.
