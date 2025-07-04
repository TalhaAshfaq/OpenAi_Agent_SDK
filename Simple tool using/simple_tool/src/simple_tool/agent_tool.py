from agents import Agent, Runner, set_default_openai_api, set_tracing_disabled, AsyncOpenAI, set_default_openai_client, function_tool
from simple_tool.my_secrets import Secret

secrets = Secret()

external_client = AsyncOpenAI(
    api_key=secrets.gemini_api_key,
    base_url=secrets.gemini_base_url,

)

set_default_openai_client(external_client)
set_tracing_disabled(True)
set_default_openai_api('chat_completions')

@function_tool("get_weather")
def get_weather(location: str) -> str:
    """
    fetch the weather for a given location, returning a short description.
    """
    return f"the weather in {location} is 22 degrees"

@function_tool("piaic_student_finder")
def student_finder(student_roll: int) -> str:
    """
    find the piaic student base on the roll no
    """
    data = {
        1: "Ali",
        2: "Asad",
        3: "Razzaq"
    }

    return data.get(student_roll, "not found")

def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        tools=[get_weather, student_finder],
        model=secrets.gemini_api_model,

    )

    result = Runner.run_sync(
        agent,
        "what's the weather in lahore now"
    )

    print(result.final_output)