
export MODE="DEV"
gcloud config set project fbe-gcp-project
gcloud functions deploy fbeToProgram --runtime python39 --trigger-http --region asia-northeast1
