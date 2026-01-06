# Cloud Computing Lab: Serverless REST API with Monitoring

A comprehensive lab for teaching serverless architecture on AWS, designed for industrial engineering master's students.

## Overview

This lab teaches students to build a complete serverless REST API system with monitoring, first using the AWS Console, then automating with Terraform.

## What's Included

### 📚 Documentation
- **lab-guide.md** - Complete step-by-step instructions for both console and Terraform implementation
- **student-instructions.md** - Student-facing lab assignment with deliverables and grading rubric
- **terraform/README.md** - Terraform-specific deployment guide

### 💻 Code
- **terraform/** - Complete Infrastructure as Code implementation
  - `main.tf` - Main Terraform configuration
  - `variables.tf` - Configurable variables
  - `outputs.tf` - Output values after deployment
  - `lambda/product_search.py` - Lambda function code
  - `website/index.html` - Static website frontend

### 🧪 Testing
- **test-api.sh** - Automated API testing script
- **sample-data.json** - Sample product data for DynamoDB

## Architecture

```
User → CloudFront (CDN) → S3 Static Website
         ↓
    WAF (Security) → API Gateway → Lambda (in VPC) → DynamoDB
                          ↓                              ↑
                    CloudWatch ←→ SNS              VPC Endpoint
                    (Monitoring)  (Alerts)         (Private Access)
```

**Production-Grade Components:**
- **CloudFront**: Global CDN for low-latency content delivery
- **WAF**: Web Application Firewall protecting API from attacks
- **VPC**: Network isolation with private subnets for Lambda
- **VPC Endpoints**: Private access to DynamoDB (no internet required)
- **SNS**: Automated email notifications for alarms
- **CloudWatch**: Comprehensive monitoring and alerting

## Use Case: Product Inventory Search

Students build a searchable product inventory system where users can:
- View all products
- Filter by category
- Search by product name
- Filter by price range
- Combine multiple filters

## Learning Objectives

1. **Serverless Architecture**: Understand event-driven, serverless computing
2. **Infrastructure as Code**: Learn Terraform for reproducible deployments
3. **API Design**: Build RESTful APIs with proper error handling
4. **Security**: Implement WAF rules and VPC network isolation
5. **CDN**: Configure CloudFront for global content delivery
6. **Monitoring**: Implement comprehensive observability with CloudWatch
7. **Notifications**: Set up automated alerts with SNS
8. **Cost Optimization**: Understand serverless pricing and VPC endpoints

## Quick Start for Instructors

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Terraform installed (for Phase 2)

### Lab Structure

**Phase 1: Console Implementation **
- Manual deployment through AWS Console
- Hands-on understanding of each service
- Immediate visual feedback

**Phase 2: Terraform Implementation **
- Automated infrastructure deployment
- Version-controlled infrastructure
- Reproducible environments

**Phase 3: Monitoring (Extra) **
- CloudWatch logs and metrics
- Dashboard creation
- Alarm configuration

### Deployment

#### For Console Lab
Follow `lab-guide.md` starting from Step 1

#### For Terraform Lab
```bash
cd terraform

# Set your email for SNS notifications
terraform apply -var="alert_email=your-email@example.com"
```

Get the outputs:
```bash
terraform output
```

**Important**: After deployment:
1. Check your email and confirm SNS subscription
2. Copy the CloudFront URL to access the website
3. The API Gateway URL is already configured in the website

### Testing

Run the test script:
```bash
./test-api.sh <API_GATEWAY_URL>
```

Or test manually:
```bash
# Get all products
curl "https://your-api-url/products"

# Filter by category
curl "https://your-api-url/products?category=Machinery"

# Search by name
curl "https://your-api-url/products?name=Drill"

# Price range
curl "https://your-api-url/products?minPrice=100&maxPrice=2000"
```

## Customization

### Change Data Type
The lab uses product inventory, but you can easily adapt it to:
- Customer database
- Order tracking system
- Equipment maintenance records
- Supply chain management
- Any searchable dataset

To customize:
1. Modify DynamoDB schema in `terraform/main.tf`
2. Update Lambda function filters in `lambda/product_search.py`
3. Adjust website UI in `website/index.html`
4. Update sample data in `sample-data.json`

### Adjust Difficulty

**Make it easier:**
- Provide pre-filled Terraform files
- Skip monitoring section
- Use fewer AWS services

**Make it harder:**
- Add authentication (Cognito)
- Implement POST/PUT/DELETE operations
- Add pagination
- Require CI/CD pipeline
- Add caching layer (ElastiCache)

## Cost Estimation

With AWS Free Tier:
- **DynamoDB**: Free (25 GB storage, 25 WCU, 25 RCU)
- **Lambda**: Free (1M requests/month)
- **API Gateway**: Free for 12 months (1M requests/month)
- **S3**: ~$0.023/GB/month
- **CloudFront**: Free for 12 months (1TB data transfer, 10M requests)
- **WAF**: ~$5/month (Web ACL) + $1 per million requests
- **SNS**: Free (1,000 email notifications/month)
- **CloudWatch**: Free tier (10 metrics, 5GB logs)
- **VPC**: Free (VPC, subnets, security groups, VPC endpoints)

**Estimated cost per student**: $5-10/month (mainly WAF)

**Cost Savings**:
- ✅ No NAT Gateway (~$32/month saved)
- ✅ Gateway VPC endpoints are free
- ✅ Serverless = pay only for usage

**Recommendation**: Have students clean up resources after completion, or disable WAF to reduce costs to ~$0-2/month.

## Grading

See `student-instructions.md` for detailed rubric.

**Summary:**
- Console Implementation: 25%
- Terraform Implementation: 25%
- Monitoring Setup: 20%
- Testing: 15%
- Lab Report: 15%

## Common Student Issues

1. **CORS Errors**: Most common issue - ensure OPTIONS method and headers are configured
2. **IAM Permissions**: Students often forget VPC execution role for Lambda
3. **VPC Cold Starts**: Lambda in VPC takes 10-15 seconds on first invocation
4. **CloudFront Caching**: Students forget to invalidate cache after updates
5. **WAF Blocking**: Overly restrictive rules may block legitimate requests
6. **SNS Confirmation**: Students must confirm email subscription
7. **VPC Endpoints**: Must be associated with correct route tables
8. **Terraform State**: Explain state management and locking

## Extension Ideas

For advanced students or bonus assignments:
- Add authentication with Cognito
- Implement CI/CD with GitHub Actions
- Add CloudFront distribution
- Implement DynamoDB Streams
- Add X-Ray tracing
- Create automated tests
- Implement blue-green deployment

## Support

### For Instructors
- Review `lab-guide.md` before assigning
- Test deployment in your AWS account
- Adjust time estimates based on student experience
- Consider providing AWS credits for students

### For Students
- Follow `student-instructions.md`
- Check `lab-guide.md` for detailed steps
- Use `test-api.sh` for API testing
- Refer to troubleshooting sections

## License

This lab material is provided for educational purposes.

## Contributing

Suggestions for improvements:
- Additional use cases
- More monitoring examples
- Advanced challenges
- Alternative implementations

## Acknowledgments

Designed for industrial engineering master's students learning cloud computing and infrastructure as code.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Tested With**: AWS Free Tier, Terraform 1.0+
