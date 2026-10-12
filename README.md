# AWS Web Crawler CRUD API

## Project Overview

This project implements a RESTful API for managing a list of websites to be crawled. Users can create, retrieve, update and delete website targets through Amazon API Gateway.

The application uses AWS Lambda to process HTTP requests and Amazon DynamoDB to store the website records.

## System Architecture

The application follows a serverless architecture:

**API Client → Amazon API Gateway → AWS Lambda → Amazon DynamoDB**

- **API Gateway:** Provides REST endpoints for managing crawler targets.
- **AWS Lambda:** Executes Python code to process CRUD requests.
- **DynamoDB:** Stores website IDs, URLs and crawl statuses.
- **GitHub:** Stores the source code, documentation and project dashboard.
- **GitHub Actions:** Runs automated Python tests when changes are pushed.

## Technologies Used

- Python 3.13
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- AWS IAM
- Boto3
- Python unittest
- GitHub Actions

## API Endpoints

The REST API provides the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/targets` | Add a website |
| GET | `/targets` | Retrieve all websites |
| GET | `/targets/{id}` | Retrieve a specific website |
| PUT | `/targets/{id}` | Update a website URL |
| DELETE | `/targets/{id}` | Delete a website |

### Example: Create a Website

**Request**

`POST /targets`

```json
{
  "url": "https://example.com"
}
```

**Response**

```json
{
  "message": "Created",
  "item": {
    "id": "generated-unique-id",
    "url": "https://example.com",
    "status": "pending"
  },
  "dynamodb_operation_ms": 40.5
}
```

The API generates a unique ID for each website and initially assigns it a `pending` status.

## DynamoDB Database

The database table is named `CrawlerTargets`.

| Attribute | Type | Description |
|---|---|---|
| id | String | Unique identifier and partition key |
| url | String | Website address |
| status | String | Crawl status |

## Testing

The project uses Python's `unittest` framework and GitHub Actions.

The initial automated test suite includes:

1. Unit test for invalid URL handling.
2. Unit test for unsupported HTTP methods.
3. Functional test for creating a website using a mocked database.
4. Mocked Lambda–DynamoDB interaction test.

All four tests passed in GitHub Actions.

Manual tests have also been performed through AWS Lambda and API Gateway to verify CRUD functionality.

A real integration test and more detailed performance testing are planned.

## Running Automated Tests

Install the Python dependency:

```bash
pip install boto3
```

Run the tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions also runs the test suite automatically when changes are pushed to the main branch.

## Deployment

The API has been deployed to the `beta` stage in AWS API Gateway in the `us-east-2` region.

### Beta API Endpoint

Base URL:
https://ajdh6czgol.execute-api.us-east-2.amazonaws.com/beta

The Lambda function `CrawlerCRUD` accesses the DynamoDB table `CrawlerTargets` using its IAM execution role.

A production stage and automated AWS CodePipeline deployments are planned.

## Security and Quality

- IAM permissions restrict Lambda access to the target DynamoDB table.
- The API validates basic URL formatting and handles invalid JSON.
- Database operations include error handling.
- DynamoDB operations use conditional checks when updating and deleting records.
- The API returns standard HTTP status codes.
- Basic operation timing is recorded in milliseconds.

The API is publicly accessible for demonstration purposes and does not currently require authentication. It should be secured before use with real or sensitive data.

## Project Status

- CRUD Lambda implementation: Complete
- DynamoDB integration: Complete
- API Gateway beta deployment: Complete
- Initial automated tests: Complete
- GitHub Project dashboard: Created
- Real integration/performance tests: In progress
- Production CI/CD: Planned

## Future Improvements

- Add authentication and authorisation.
- Improve URL validation.
- Implement the actual crawling and content extraction process.
- Automate beta and production deployments.
- Add more comprehensive performance and reliability testing.
