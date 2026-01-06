# Student Lab Instructions: Serverless REST API with Monitoring

## Lab Objectives

By the end of this lab, you will:
1. Deploy a complete serverless REST API using AWS services
2. Implement monitoring and observability with CloudWatch
3. Automate infrastructure deployment using Terraform
4. Understand serverless architecture patterns

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Terraform installed (for Phase 2)
- Basic understanding of REST APIs, databases, and cloud computing

## Lab Duration

- Phase 1 (Console): 2-3 hours
- Phase 2 (Terraform): 1-2 hours
- Total: 3-5 hours

## What You'll Build

A **Product Inventory Search System** with:
- Static website hosted on S3
- REST API via API Gateway
- Lambda function for business logic
- DynamoDB for data storage
- CloudWatch for monitoring and logging

## Architecture Diagram

```
┌─────────┐      ┌─────────────┐      ┌──────────────┐      ┌────────┐      ┌──────────┐
│  User   │─────▶│  S3 Static  │─────▶│ API Gateway  │─────▶│ Lambda │─────▶│ DynamoDB │
│ Browser │      │   Website   │      │  (REST API)  │      │Function│      │  Table   │
└─────────┘      └─────────────┘      └──────────────┘      └────────┘      └──────────┘
                                              │                    │
                                              │                    │
                                              ▼                    ▼
                                       ┌──────────────────────────────┐
                                       │   CloudWatch Logs & Metrics  │
                                       └──────────────────────────────┘
```

## Phase 1: Console Implementation

Follow the detailed steps in `lab-guide.md` to:

### Part A: Backend Setup (Steps 1-7)
1. Create DynamoDB table
2. Add sample product data
3. Create Lambda function
4. Configure IAM permissions
5. Create API Gateway
6. Configure API methods and CORS
7. Deploy API

### Part B: Frontend Setup (Steps 8-11)
8. Create S3 bucket
9. Enable static website hosting
10. Configure bucket policy
11. Upload website files

### Part C: Monitoring Setup (Steps 12-17)
12. Enable Lambda CloudWatch logs
13. Enable API Gateway logs
14. Create CloudWatch dashboard
15. Create CloudWatch alarms
16. View logs and metrics
17. Test monitoring

## Phase 2: Terraform Implementation

Follow the Terraform guide in `terraform/README.md` to:

### Part A: Setup (Steps 18-20)
18. Clean up console resources (optional)
19. Install Terraform
20. Configure AWS CLI

### Part B: Deployment (Steps 21-24)
21. Review Terraform configuration
22. Initialize Terraform
23. Apply configuration
24. Update website with API URL

## Deliverables

### 1. Screenshots (Required)

Capture and submit screenshots of:
- [ ] DynamoDB table with sample data
- [ ] Lambda function code
- [ ] API Gateway configuration
- [ ] S3 bucket with static website
- [ ] Working website showing search results
- [ ] CloudWatch dashboard with metrics
- [ ] CloudWatch logs showing API calls
- [ ] Terraform apply output
- [ ] Terraform outputs showing URLs

### 2. Testing Results (Required)

Document your testing:
- [ ] Test all search filters (category, name, price range)
- [ ] Test combined filters
- [ ] Run the `test-api.sh` script and save output
- [ ] Show API response times in CloudWatch
- [ ] Demonstrate alarm triggering (optional)

### 3. Lab Report (Required)

Write a report (2-3 pages) covering:

**Section 1: Architecture Analysis**
- Describe the serverless architecture
- Explain data flow from user to database
- Discuss advantages and limitations

**Section 2: Implementation Experience**
- Challenges faced during console implementation
- Differences between console and Terraform approaches
- Time comparison between both methods

**Section 3: Monitoring Insights**
- Key metrics observed
- Log analysis findings
- Recommendations for production monitoring

**Section 4: Cost Analysis**
- Estimate monthly costs for this architecture
- Identify cost optimization opportunities
- Compare with traditional server-based approach

### 4. Code Submission (Required)

Submit:
- [ ] Modified `index.html` with your API URL
- [ ] Lambda function code (if modified)
- [ ] Terraform configuration files
- [ ] Any custom scripts created

## Grading Rubric

| Component | Points | Criteria |
|-----------|--------|----------|
| Console Implementation | 25 | All services deployed correctly, website functional |
| Terraform Implementation | 25 | Infrastructure automated, reproducible deployment |
| Monitoring Setup | 20 | Logs, metrics, dashboard, and alarms configured |
| Testing | 15 | Comprehensive testing documented with evidence |
| Lab Report | 15 | Clear analysis, insights, and recommendations |

**Total: 100 points**

## Common Issues and Solutions

### Issue 1: CORS Errors
**Symptom**: Website can't connect to API
**Solution**: 
- Verify OPTIONS method is configured
- Check Lambda returns CORS headers
- Ensure API Gateway CORS is enabled

### Issue 2: Lambda Permission Denied
**Symptom**: API returns 500 error
**Solution**:
- Check IAM role has DynamoDB permissions
- Verify Lambda execution role is attached

### Issue 3: S3 Website 403 Forbidden
**Symptom**: Can't access website
**Solution**:
- Unblock public access in bucket settings
- Add bucket policy for public read
- Verify static website hosting is enabled

### Issue 4: Terraform State Lock
**Symptom**: Terraform apply fails with lock error
**Solution**:
```bash
terraform force-unlock <LOCK_ID>
```

### Issue 5: API Gateway 403 Error
**Symptom**: API calls return 403
**Solution**:
- Check Lambda permission for API Gateway
- Verify API is deployed to correct stage
- Test Lambda function directly first

## Tips for Success

1. **Start Early**: Don't wait until the deadline
2. **Test Incrementally**: Test each component before moving to the next
3. **Document As You Go**: Take screenshots during implementation
4. **Use CloudWatch**: Check logs immediately when something fails
5. **Clean Up**: Delete resources after completion to avoid charges
6. **Ask Questions**: Use office hours if stuck

## Extension Challenges (Bonus Points)

For extra credit, implement any of these:

1. **Authentication** (+5 points)
   - Add API key authentication to API Gateway
   - Implement Cognito user authentication

2. **Advanced Monitoring** (+5 points)
   - Add X-Ray tracing
   - Create custom CloudWatch metrics
   - Set up SNS notifications for alarms

3. **Performance Optimization** (+5 points)
   - Add CloudFront distribution
   - Implement DynamoDB caching
   - Optimize Lambda cold starts

4. **CI/CD Pipeline** (+10 points)
   - Create GitHub Actions workflow
   - Automate testing and deployment
   - Implement blue-green deployment

5. **Enhanced Features** (+5 points)
   - Add POST endpoint to create products
   - Implement pagination
   - Add sorting options

## Resources

### AWS Documentation
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [CloudWatch User Guide](https://docs.aws.amazon.com/cloudwatch/)

### Terraform
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

### Tutorials
- [Serverless Architectures on AWS](https://aws.amazon.com/serverless/)
- [Building REST APIs with Lambda](https://aws.amazon.com/getting-started/hands-on/build-serverless-web-app-lambda-apigateway-s3-dynamodb-cognito/)

## Submission Instructions

1. Create a ZIP file containing:
   - Lab report (PDF)
   - Screenshots folder
   - Code files
   - Testing results

2. Name the file: `LastName_FirstName_CloudLab.zip`

3. Submit via the course portal by the deadline

4. Include a README.txt with:
   - Your name and student ID
   - Date of completion
   - Any special notes or issues encountered

## Academic Integrity

- You may discuss concepts with classmates
- All code and reports must be your own work
- Cite any external resources used
- Do not share your AWS credentials

## Questions?

Contact:
- Instructor: [Your Email]
- Office Hours: [Times]
- Discussion Forum: [Link]

Good luck! 🚀
