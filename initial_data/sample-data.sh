aws dynamodb batch-write-item --request-items '{
  "ProductInventory": [
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD020"},
      "name": {"S": "Ear Protection"},
      "category": {"S": "Safety Equipment"},
      "price": {"N": "15.99"},
      "stock": {"N": "400"},
      "manufacturer": {"S": "SafetyFirst"},
      "lastUpdated": {"S": "2026-01-07"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD021"},
      "name": {"S": "CNC Machine"},
      "category": {"S": "Machinery"},
      "price": {"N": "25000.00"},
      "stock": {"N": "1"},
      "manufacturer": {"S": "PrecisionTech"},
      "lastUpdated": {"S": "2026-01-02"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD022"},
      "name": {"S": "PVC Pipes"},
      "category": {"S": "Materials"},
      "price": {"N": "28.50"},
      "stock": {"N": "350"},
      "manufacturer": {"S": "PlumbSupply"},
      "lastUpdated": {"S": "2026-01-06"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD023"},
      "name": {"S": "Torque Wrench"},
      "category": {"S": "Tools"},
      "price": {"N": "145.00"},
      "stock": {"N": "22"},
      "manufacturer": {"S": "ToolCorp"},
      "lastUpdated": {"S": "2026-01-05"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD024"},
      "name": {"S": "Respirator Mask"},
      "category": {"S": "Safety Equipment"},
      "price": {"N": "35.99"},
      "stock": {"N": "180"},
      "manufacturer": {"S": "SafetyFirst"},
      "lastUpdated": {"S": "2026-01-07"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD025"},
      "name": {"S": "Air Compressor"},
      "category": {"S": "Machinery"},
      "price": {"N": "1800.00"},
      "stock": {"N": "7"},
      "manufacturer": {"S": "PowerTools"},
      "lastUpdated": {"S": "2026-01-04"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD026"},
      "name": {"S": "Cement Bags"},
      "category": {"S": "Materials"},
      "price": {"N": "12.50"},
      "stock": {"N": "500"},
      "manufacturer": {"S": "BuildMaster"},
      "lastUpdated": {"S": "2026-01-07"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD027"},
      "name": {"S": "Jigsaw"},
      "category": {"S": "Tools"},
      "price": {"N": "95.00"},
      "stock": {"N": "35"},
      "manufacturer": {"S": "ToolCorp"},
      "lastUpdated": {"S": "2026-01-06"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD028"},
      "name": {"S": "Safety Harness"},
      "category": {"S": "Safety Equipment"},
      "price": {"N": "125.00"},
      "stock": {"N": "75"},
      "manufacturer": {"S": "SafetyFirst"},
      "lastUpdated": {"S": "2026-01-05"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD029"},
      "name": {"S": "Laser Level"},
      "category": {"S": "Tools"},
      "price": {"N": "280.00"},
      "stock": {"N": "14"},
      "manufacturer": {"S": "PrecisionTech"},
      "lastUpdated": {"S": "2026-01-07"}
    }}},
    { "PutRequest": { "Item": {
      "productId": {"S": "PROD030"},
      "name": {"S": "Industrial Generator"},
      "category": {"S": "Machinery"},
      "price": {"N": "12000.00"},
      "stock": {"N": "2"},
      "manufacturer": {"S": "PowerTools"},
      "lastUpdated": {"S": "2026-01-03"}
    }}}
  ]
}'
