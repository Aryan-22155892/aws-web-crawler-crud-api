
import json
import os
import uuid
import time
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(
    os.environ.get("TABLE_NAME", "CrawlerTargets")
)

def response(status, data):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(data)
    }

def lambda_handler(event, context):
    method = event.get("httpMethod")

    # Supports API Gateway HTTP API as well
    if not method:
        method = event.get(
            "requestContext", {}
        ).get("http", {}).get("method")

    method = (method or "").upper()
    params = event.get("pathParameters") or {}
    target_id = params.get("id")

    try:
        body = json.loads(event.get("body") or "{}")
        if not isinstance(body, dict):
            return response(400, {"error": "Invalid body"})
    except (ValueError, TypeError):
        return response(400, {"error": "Invalid JSON"})

    try:
        start = time.perf_counter()

        if method == "POST":
            url = body.get("url")
            if not isinstance(url, str) or not url.startswith(
                ("http://", "https://")
            ):
                return response(400, {"error": "Valid URL required"})

            item = {
                "id": str(uuid.uuid4()),
                "url": url,
                "status": "pending"
            }
            write_start = time.perf_counter()
            table.put_item(Item=item)
            write_time_ms = round((time.perf_counter() - write_start) * 1000, 2)
            result = response(201, {
                "message": "Created",
                "item": item,
                "dynamodb_write_ms": write_time_ms
            })

        elif method == "GET": 
            if target_id:
                read_start = time.perf_counter()
                result_data = table.get_item(
                    Key={"id": target_id}
                ).get("Item")
                read_time_ms = round(
                    (time.perf_counter() - read_start) * 1000, 2
                )
                if not result_data:
                    return response(404, {"error": "Not found"})
                result = response(200, {
                    **result_data,
                    "dynamodb_read_ms": read_time_ms
                })
            else:
                items = []
                scan_args = {}
                while True:
                    page = table.scan(**scan_args)
                    items.extend(page.get("Items", []))
                    if "LastEvaluatedKey" not in page:
                        break
                    scan_args["ExclusiveStartKey"] = page["LastEvaluatedKey"]
                result = response(200, {"items": items})

        elif method == "PUT":
            if not target_id:
                return response(400, {"error": "ID required"})
            url = body.get("url")
            if not isinstance(url, str) or not url.startswith(
                ("http://", "https://")
            ):
                return response(400, {"error": "Valid URL required"})

            try:
                updated = table.update_item(
                    Key={"id": target_id},
                    UpdateExpression="SET #u = :url",
                    ConditionExpression="attribute_exists(id)",
                    ExpressionAttributeNames={"#u": "url"},
                    ExpressionAttributeValues={":url": url},
                    ReturnValues="ALL_NEW"
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    return response(404, {"error": "Not found"})
                raise
            result = response(200, {
                "message": "Updated",
                "item": updated["Attributes"]
            })

        elif method == "DELETE":
            if not target_id:
                return response(400, {"error": "ID required"})
            try:
                table.delete_item(
                    Key={"id": target_id},
                    ConditionExpression="attribute_exists(id)"
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    return response(404, {"error": "Not found"})
                raise
            result = response(200, {"message": "Deleted"})

        else:
            return response(405, {"error": "Method not allowed"})

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        result_body = json.loads(result["body"])
        result_body["dynamodb_operation_ms"] = elapsed_ms
        result["body"] = json.dumps(result_body)
        return result

    except ClientError as e:
        print("DynamoDB error:", e.response["Error"]["Code"])
        return response(500, {"error": "Database operation failed"})
    except Exception as e:
        print("Unexpected error:", str(e))
        return response(500, {"error": "Internal server error"})
