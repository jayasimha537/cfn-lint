### Roadmap
- Be able to test transforms (serverless, include)
- Add tests around common resource types
  - AutoScaling
  - Ec2 Instances
  - Load Balancers
  - RDS
- Create a framework to test ARNs
- Test Ref resources to IAM Roles have good assume role documents.  Example: Lambda Function Ref refers to an IAM Role that can be assume by Lambda.
- More Warnings around hard coded values (Regions, AccountIds) to help with the practice of reusability

### 0.0.8
###### Features
- Added a rule to check for only one resource property in a set
- Added a rule for more than one of resource properties in a set
- Added a rule for mutually exclusive resource properties

###### Fixes
- Support parsing JSON files that have tabs
- Better error handling for when a property is a list instead of an object
- Error handling for when files can't be read or don't exist

### 0.0.7
###### Features
- Fix for supporting more parameter types when checking REFs to parameters for Security Groups

### 0.0.6
###### Features
- Exit code non zero on errors or warnings

### 0.0.5
###### Features
- Testing CloudFormation resources against the Resource Spec
- Test Functions against supported included functions
- Test overall CloudFormation structure
- Test Regionalization of a template against the Resource Spec
- Ability to add additional rules on parameter
- In depth checks of values around AWS::EC2::VPC, AWS::EC2::Subnet, and AWS::EC2::SecurityGroup