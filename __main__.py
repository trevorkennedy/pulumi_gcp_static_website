import os
import pulumi
from pulumi_gcp import storage

# Create a GCP resource (Storage Bucket)
bucket = storage.Bucket("static-website",
                        cors=[storage.BucketCorArgs(
                            max_age_seconds=3600,
                            methods=[
                                "GET",
                                "HEAD",
                                "PUT",
                                "POST",
                                "DELETE",
                            ],
                            origins=["http://example.com"],
                            response_headers=["*"],
                        )],
                        force_destroy=True,
                        uniform_bucket_level_access=True,
                        website=storage.BucketWebsiteArgs(
                            main_page_suffix="index.html",
                            not_found_page="404.html",
                        ))

# Set public access policy for the bucket
storage.BucketIAMBinding('my-bucket-IAMBinding',
                         bucket=bucket,
                         role="roles/storage.objectViewer",
                         members=["allUsers"]
                         )

# Upload files to bucket
for subdir, dirs, files in os.walk('site'):
    for file in files:
        local_path = os.path.join(subdir, file)
        remote_path = local_path.replace('site/', '')
        storage.BucketObject(
            remote_path,
            name=remote_path,
            bucket=bucket,
            content_type='text/html',
            source=pulumi.FileAsset(local_path)
        )

# Export the DNS name of the bucket
pulumi.export('bucket_name', bucket.url)
pulumi.export('bucket_endpoint',
              pulumi.Output.concat('http://storage.googleapis.com/', bucket.id)
              )
