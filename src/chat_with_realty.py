from dotenv import load_dotenv
from src.prompts.realty_v1 import SYSTEM_PROMPT, USER_PROMPT
from src.chat_handlers.realty_handler import RealtyAgent
from openai import OpenAI
from os import environ

def welcome_realty():
    """Custom welcome screen for Realty chatbot"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ███████╗ █████╗ ██╗  ████████╗██╗   ██╗         ║
║   ██╔══██╗██╔════╝██╔══██╗██║  ╚══██╔══╝╚██╗ ██╔╝         ║
║   ██████╔╝█████╗  ███████║██║     ██║    ╚████╔╝          ║
║   ██╔══██╗██╔══╝  ██╔══██║██║     ██║     ╚██╔╝           ║
║   ██║  ██║███████╗██║  ██║███████╗██║      ██║            ║
║   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═╝            ║
║                                                           ║
║              HI! CHAT WITH REALTY BELOW                   ║
║           Your AI Real Estate Assistant 🏠                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

def get_user_input():
    user_input = input("User: ")
    return user_input


def main():

    # We want code to fail loudly if API key is not set.
    llm_client = OpenAI(api_key=environ['OPENAI_API_KEY'])
     
    welcome_realty()

    # TODO: Update chat_ended to be dynamically set by Realty's decision.
    should_chat_end = False

    chat_history = []

    re_agent = RealtyAgent(
        system_prompt_template=SYSTEM_PROMPT,
        user_prompt_template=USER_PROMPT,
        llm_client=llm_client
    )

    while not should_chat_end:
        curr_user_turn = get_user_input()

        # TODO: remove later, for now simulating exitting chat.

        agent_response, should_chat_end = re_agent.get_agent_response(
            user_message=curr_user_turn,
            chat_history=chat_history,
            should_chat_end=should_chat_end
        )

        print(f'Realty: {agent_response}')

        if agent_response == 'quit':
            should_chat_end = True


    print('\n\nEXITING CHAT WITH REALTY.\n\n')




if __name__ == "__main__":
    # Ensure credentials are loaded securely.
    load_dotenv('.env')
    main()
