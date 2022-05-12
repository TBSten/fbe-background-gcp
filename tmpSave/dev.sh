
export GOOGLE_APPLICATION_CREDENTIALS="/Users/tsubasa/Desktop/dev/fbe/backend-gcp/tmpSave/secrets/fbe-gcp-project-f5813f02091f.json"
tsc
concurrently "tsc -w" "npx functions-framework --target=tmpSave --port=8080"
