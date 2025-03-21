import os
import chainlit as cl
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

provider = AsyncOpenAI(
  api_key = GOOGLE_API_KEY,
  base_url = "https://generativelanguage.googleapis.com/v1beta/openai/" 
)
model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client = provider,
)
run_config = RunConfig(
    model = model,
    model_provider = provider,
    tracing_disabled = True)
agent1 = Agent(
    instructions = "You are a helpfull assistant that can answer questions and help with tasks",
    name = "My Support Agent"
)
@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hello! iam the supporf sgent").send()

@cl.on_message
async def handle_message(message: cl.Message): 
    history = cl.user_session.get("history")
    history.append({"role":"user", "content": message.content})
    msg = cl.Message(content="")
    await msg.send()
    result = Runner.run_streamed(
            agent1,
            input = history,
            run_config = run_config,

    )
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
        #    
            await msg.stream_token(event.data.delta)

    history.append({"role":"assistant", "content":result.final_output})
    cl.user_session.set("history", history)
   

 