# AWS_RAG_Application

Welcome to the AWS_RAG_Application! This project is a Retrieval-Augmented Generation (RAG) application that uses Streamlit for uploading PDFs, creating vector embeddings using Faiss Database, storing the embeddings in an S3 Bucket, and then retrieving the embeddings to ask questions about the content.

## Features

- Upload PDF files
- Create vector embeddings using Faiss Database
- Store embeddings in AWS S3 Bucket
- Retrieve embeddings for question answering
- Simple and interactive user interface with Streamlit

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/HarshvardhanPandey2003/AWS_RAG_Application.git
    ```

2. Navigate to the project directory:
    ```sh
    cd AWS_RAG_Application
    ```

3. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

5. Configure your AWS credentials for accessing S3.

6. Start the Streamlit application:
    ```sh
    streamlit run Main.py
    ```

7. Open your web browser and go to `http://localhost:8501/`.

## Usage

- **Upload PDF:** Use the Streamlit interface to upload PDF files.
- **Create Embeddings:** The application will automatically create vector embeddings for the uploaded PDF using Faiss Database.
- **Store in S3:** The embeddings will be stored in the configured AWS S3 Bucket.
- **Ask Questions:** Retrieve the embeddings and ask questions about the content using the interactive interface.

## Folder Structure

```sh
AWS_RAG_Application/
├── Admin/
│   └── Admin.py
├── User/
│   └── User.py
├── data/
│   └── (uploaded PDFs and other data files)
├── Main.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/YourFeature`)
3. Commit your Changes (`git commit -m 'Add some YourFeature'`)
4. Push to the Branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Harshvardhan Pandey -(mailto:harshvardhanpandey2003@gmail.com)

Project Link: [https://github.com/HarshvardhanPandey2003/AWS_RAG_Application](https://github.com/HarshvardhanPandey2003/AWS_RAG_Application)

---

Thank you for using the AWS_RAG_Application! We hope it meets your needs. If you have any questions or feedback, feel free to reach out.
