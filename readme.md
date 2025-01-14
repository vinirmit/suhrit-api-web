Run the command

python -m pip install pymongo -t ./ to install the package locally before deploying the zip file on AWS console.


Setting Up Cognito with Google Identity provider
https://repost.aws/knowledge-center/cognito-google-social-identity-provider

- Create a new User pool with a Single Page Application client
- Create a Client in Google Cloud https://console.cloud.google.com/apis/credentials


Adding an Authorizer
Type - JWT
Name - As per the environment
Identity source - $request.header.Authorization
Issuer URL - Cognito URL https://cognito-idp.<region>.amazonaws.com/<pool-id>
Audience - Client Id of the SPA application created in the User Pool
