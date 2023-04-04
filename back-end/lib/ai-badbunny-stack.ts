import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';

export class AIBadBunnyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Defines an on-demand DynamoDB Table to index conversation index with the phone number
    const conversationIndexTable = new dynamodb.Table(this, 'ConversationIndexTable', {
      partitionKey: { name: 'phone_number', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    // Defines a DynamoDB Table to store conversations
    const conversationTable = new dynamodb.Table(this, 'ConversationTable', {
      partitionKey: { name: 'SessionId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    // Defines a Python Lambda resource AIMessageProcessor that has a function
    const AIMessageProcessor = new lambda.Function(this, 'AIMessageProcessor', {
      runtime: lambda.Runtime.PYTHON_3_9,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'AIMessageProcessor.lambda_handler',
      timeout: cdk.Duration.seconds(120),
      architecture: lambda.Architecture.ARM_64,
    });

    const lambdaUrl = AIMessageProcessor.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    });

    // Add requests lambda layer to AIMessageProcessor
    const requestsLayer = lambda.LayerVersion.fromLayerVersionArn(this, 'requestsLayer', 'arn:aws:lambda:us-east-1:377190169022:layer:requests:2');
    AIMessageProcessor.addLayers(requestsLayer);

    const langchainLayer = lambda.LayerVersion.fromLayerVersionArn(this, 'langchainLayer', 'arn:aws:lambda:us-east-1:609061237212:layer:langchain:6');
    AIMessageProcessor.addLayers(langchainLayer);

    // Grant Lambda function access to DynamoDB tables
    conversationIndexTable.grantReadWriteData(AIMessageProcessor);
    conversationTable.grantReadWriteData(AIMessageProcessor);

    // Stores OpenAI API key in AWS SSM Parameter Store
    const openAIKey = new ssm.StringParameter(this, 'OpenAIKey', {
      description: 'OpenAI API Key',
      stringValue: process.env.OPENAI_API_KEY!,
    });

    // Grant Lambda function role access to read OpenAI API key from SSM Parameter Store
    const ssmPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['ssm:GetParameter'],
      resources: [openAIKey.parameterArn]
    });

    AIMessageProcessor.addToRolePolicy(ssmPolicy);

    // Pass SSM parameter name to Lambda function
    AIMessageProcessor.addEnvironment('OPENAI_API_KEY_SSM_PARAMETER_NAME', openAIKey.parameterName);

    // Pass DynamoDB table names to Lambda function
    AIMessageProcessor.addEnvironment('CONVERSATION_INDEX_TABLE_NAME', conversationIndexTable.tableName);
    AIMessageProcessor.addEnvironment('CONVERSATION_TABLE_NAME', conversationTable.tableName);

    // Pass TicketMaster API key to Lambda function
    AIMessageProcessor.addEnvironment('TICKET_MASTER_API_KEY', process.env.TICKET_MASTER_API_KEY!);

    new cdk.CfnOutput(this, 'FunctionUrl', {
      value: lambdaUrl.url,
    })
  }
}
