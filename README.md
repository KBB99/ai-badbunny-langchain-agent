# AI Bad Bunny. Langchain, AWS, and LLMs

Medium Article: [Creating Dynamic AI Agents With Langchain, OpenAI’s GPT-4, and AWS
](https://medium.com/better-programming/creating-dynamic-ai-agents-with-langchain-openais-gpt-4-and-aws-building-the-ai-bad-bunny-event-74208b26f46f)

To get the project up and running, you need to have the following installed:

CDK
AWS CLI
NodeJS
Python 3.6

Once you have the above installed, you can run the following commands to get the back-end up and running:

```bash
cd backend
npm i
export OPENAI_API_KEY=<your-openai-api-key>
export TICKET_MASTER_API_KEY=<your-ticket-master-api-key>
npx cdk deploy
```

Save the API Gateway URL that is outputted by the above command. You will need it to run the front-end.

Once the backend is deployed, you can run the following commands to get the front-end up and running:

```bash
cd ..
git clone https://github.com/KBB99/ai-chat-next-amplify
cd ai-chat-next-amplify
echo "LAMBDA_URL=<your-lambda-url>" > .env.local
npm i
npm run dev
```

