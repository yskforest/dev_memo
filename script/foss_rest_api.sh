#/bin/bash

URL_API=http://XXX:8081/repo/api/v1
TOKEN=XXX
FOSS_FOLDER_NAME=XXX
UPLOAD_FILE=XXX.tar.gz

# フォルダ一覧取得
curl -sS -X GET ${URL_API}/folders -H "Authorization: Bearer ${TOKEN}" | jq

# フォルダ作成
curl -sS -X POST ${URL_API}/folders \
  -H "parentFolder: 1" \
  -H "folderName: ${FOSS_FOLDER_NAME}" \
  -H "Authorization: Bearer ${TOKEN}" | jq

curl -sS -X GET ${URL_API}/folders -H "Authorization: Bearer ${TOKEN}" | jq

FOLDER_ID=$(curl -sS -X GET ${URL_API}/folders \
  -H "Authorization: Bearer ${TOKEN}" | jq -r ".[] | select(.name==\"${FOSS_FOLDER_NAME}\") | .id")

echo "Target folder ID: ${FOLDER_ID}"

curl -sS -X POST ${URL_API}/uploads \
  -H "folderId: ${FOLDER_ID}" \
  -H "uploadDescription: created by REST" \
  -H "uploadType: file" \
  -H "public: public" \
  -H "Content-Type: multipart/form-data" \
  -F "fileInput=@${UPLOAD_FILE};type=application/octet-stream" \
  -H "Authorization: Bearer ${TOKEN}" | jq

curl -sS -X GET ${URL_API}/jobs?uploads=${FOLDER_ID} \
  -H "Authorization: Bearer ${TOKEN}" | jq
