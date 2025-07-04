from agents import Agent, function_tool, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from my_secrets import Secret
secrets = Secret()
import chainlit as cl
import json
from openai.types.responses import ResponseTextDeltaEvent


external_client = AsyncOpenAI(
    api_key=secrets.gemini_api_key,
    base_url=secrets.gemini_base_url,

    )

set_default_openai_api("chat_completions")
set_default_openai_client(external_client)
set_tracing_disabled(True)

model = OpenAIChatCompletionsModel(
    model=secrets.gemini_api_model,
    openai_client=external_client
    )

@function_tool("get_weather")
def get_weather(location: str) -> str:
    """
    fetch the weather for a given location, returning a short description.
    """
    return f"the weather in {location} is 22 degrees"

agent = Agent(
        name= "Assistant",
        instructions="You are a helpful Agent, use get_weather tool to get temprature for any location",
        model=model,
        tools=[get_weather]
    )



@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history",[])
    await cl.Message(content="Hello i am the PIAIC Support Agent, how can i help you?").send() 

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    msg = cl.Message(content="")
    await msg.send()

    history.append({"role": "user", "content": message.content})

    result = Runner.run_streamed(
        starting_agent = agent,
        input = history,

    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
           

    history.append({"role": "assistant", "content": result.final_output})
    #await cl.Message(content=result.final_output).send()

    with open("history.json", "w") as f:
        json.dump(history, f, indent=4)