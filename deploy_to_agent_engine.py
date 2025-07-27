import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv
from finara_agent.agent import get_finara_coordinator
from google.oauth2 import service_account

load_dotenv()
sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
credentials = service_account.Credentials.from_service_account_file(sa_path)

bucket_uri = os.getenv("STAGING_BUCKET", "gs://geni-project_cloudbuild")
bucket_name = bucket_uri.replace("gs://", "")
from google.cloud import storage
gcs_client = storage.Client(credentials=credentials)

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=bucket_uri,
    credentials=credentials,
)

print(f"Using service account: {credentials.service_account_email}")

from google.cloud.exceptions import Forbidden

# ✅ Optional: test GCS access before deploying agent
def validate_gcs_access():
    client = storage.Client(credentials=credentials)
    test_blob_name = "adk-upload-test.txt"

    try:
        bucket = client.bucket(bucket_name)

        # Check IAM permission for write access
        permissions = bucket.test_iam_permissions(["storage.objects.create"])
        if "storage.objects.create" not in permissions:
            raise PermissionError(f"❌ Service account does not have 'storage.objects.create' permission on bucket {bucket_name}")

        # Proceed with test upload
        blob = bucket.blob(test_blob_name)
        with blob.open("w") as f:
            f.write("This is a test file to verify GCS permissions.")
        print(f"✅ Successfully uploaded test file to {bucket_name}")
        blob.delete()
        print(f"🧹 Test file cleaned up")
    except Exception as e:
        print(f"❌ Failed GCS access check: {e}")
        exit(1)

if os.getenv("VALIDATE_GCS", "false").lower() == "true":
    validate_gcs_access()

# Additional check for bucket accessibility using HEAD request
try:
    bucket = gcs_client.bucket(bucket_name)
    test_blob = bucket.blob("permission_probe.txt")
    test_blob.upload_from_string("validate permissions")
    test_blob.delete()
    print("✅ Verified: Service account has upload/delete permissions on the bucket.")
except Exception as e:
    print(f"❌ Additional GCS write test failed: {e}")
    exit(1)

try:
    # Confirm bucket exists
    # (gcs_client and bucket_name already defined above)
    if not gcs_client.bucket(bucket_name).exists():
        raise Exception(f"❌ Bucket '{bucket_name}' not found or not accessible by the service account.")

    existing_engines = list(agent_engines.list())
    app_name = os.getenv("APP_NAME", "Agent App")

    for engine in existing_engines:
        if engine.display_name == app_name:
            print(f"✅ AgentEngine with display name '{app_name}' already exists: {engine.name}")
            exit(0)

    # Proceed with deployment
    remote_app = agent_engines.create(
        display_name=os.getenv("APP_NAME", "Agent App"),
        agent_engine=get_finara_coordinator,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            "cloudpickle==3.1.1"
        ]
    )
except Forbidden as e:
    print(f"❌ GCS write permission denied: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Failed to deploy agent engine: {e}")
    exit(1)