# AWS_RAG_Application

Welcome to the AWS RAG (Retrieval-Augmented Generation) Application! This project leverages Streamlit for an interactive user interface, Faiss for creating vector embeddings, and AWS services like S3 and DynamoDB for storage and feedback management.

## Features

- Upload PDF documents
- Generate vector embeddings using Faiss
- Store embeddings in an S3 bucket
- Retrieve and ask questions about the embeddings
- Collect user feedback and store it in DynamoDB
- Use feedback to improve responses

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

5. Set up your AWS credentials and configure your environment. Ensure you have access to S3 and DynamoDB.

6. Start the Streamlit application:
    ```sh
    streamlit run Main.py
    ```

## Usage

1. **Upload PDF:** Users can upload PDF documents via the Streamlit interface.
2. **Generate Embeddings:** The application generates vector embeddings for the uploaded PDF using Faiss and stores them in an S3 bucket.
3. **Ask Questions:** Users can ask questions about the content of the uploaded PDFs. The application retrieves relevant embeddings and generates responses.
4. **User Feedback:** Users can provide feedback on the responses. This feedback is stored in DynamoDB and used to improve future responses.

## Folder Structure

```sh
AWS_RAG_Application/
├── Admin/
│   └── Admin.py
├── User/
│   └── User.py
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

Harshvardhan Pandey - [your.email@example.com](mailto:harshvardhanpandey2003@example.com)

Project Link: [https://github.com/HarshvardhanPandey2003/AWS_RAG_Application](https://github.com/HarshvardhanPandey2003/AWS_RAG_Application)

---

Thank you for using our AWS RAG Application! We hope it meets your needs. If you have any questions or feedback, feel free to reach out.
