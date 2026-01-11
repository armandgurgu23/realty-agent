

class RealtyAgent(object):
    # TODO: Add a proper dataclass after.
    def __init__(self, system_prompt_template:str, user_prompt_template:str):
        self.system_prompt_template = system_prompt_template
        self.user_prompt_template = user_prompt_template

    def get_agent_response(self, user_message:str, chat_history:list[dict], should_chat_end:bool):
        # print(user_message)
        # print(chat_history)
        # print(should_chat_end)
        # TODO: Fill in logic with chatbot logic here. For now echoing back the user written message.
        return f"{user_message}", should_chat_end

