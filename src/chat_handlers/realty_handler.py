from openai import OpenAI
import json

class RealtyAgent(object):
    # TODO: Add a proper dataclass after.
    def __init__(self, system_prompt_template:str, user_prompt_template:str, llm_client:OpenAI):
        self.system_prompt_template = system_prompt_template
        self.user_prompt_template = user_prompt_template
        # Client + Modelling parameters.
        self.llm_client = llm_client
        self.model_snapshot = 'gpt-4.1-mini-2025-04-14'
        self.model_temperature = 0.0


    def get_agent_response(self, user_message:str, chat_history:list[dict], should_chat_end:bool):
        # print(user_message)
        # print(chat_history)
        # print(should_chat_end)
        # TODO: Fill in logic with chatbot logic here. For now echoing back the user written message.
        oai_user_message = self.prepare_oai_user_message_from_history(chat_history, user_message)

        oai_messages = self.prepare_oai_messages(
            system_prompt_template=self.system_prompt_template,
            oai_user_message=oai_user_message
        )

        oai_request_params = {
            'model': self.model_snapshot,
            'input': oai_messages,
            'temperature': self.model_temperature,
            'tools': self.prepare_tool_definitions(),
            'text': { "format": self.prepare_response_schema()}
        }

        response = self.make_openai_request(oai_request_params)


        if len(response['output']) == 1 and response['output'][0]['type'] == 'message':
            agent_message, should_chat_end = self.parse_chat_message_from_output(response['output'][0])
        else:
            # We received a tool call so we need to execute the tool and then make another
            # LLM request to interpret tool outputs.
            breakpoint()

        return f"{agent_message}", should_chat_end
    
    def parse_chat_message_from_output(self, output_message):
        try:
            chat_response_json = json.loads(output_message['content'][0]['text'])
        except:
            breakpoint()
        return chat_response_json['msg'], chat_response_json['should_chat_end']
    
    
    def prepare_tool_definitions(self):
        return None
    
    def prepare_response_schema(self):
        return {
            "type": "json_schema",
            "name": "chat_response_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "msg": {
                        "type": "string",
                        "description": "The message representing the response to user's latest intent."
                    },
                    "should_chat_end": {
                        "type": "boolean",
                        "description": "This field should be set to true when the conversation has reached a natural conclusion state."
                    }
                },
                "required": ["msg", "should_chat_end"],
                "additionalProperties": False,
            },
            "strict": True
        }
    
    def prepare_oai_messages(self, system_prompt_template:str, oai_user_message:str):
        return [
            {'role': 'system', 'content': system_prompt_template},
            {'role': 'user', 'content': oai_user_message}
        ]

    
    def prepare_oai_user_message_from_history(self, chat_history:list[dict], user_message:str) -> str:

        transcript = None

        if not chat_history:
            transcript = f'USER: {user_message}'
        
        if not transcript:
            # This is a multi-turn transcript, need to combine chat history with latest user message.
            breakpoint()
            print('Handle multi-turn.')

        formatted_user_message = self.user_prompt_template.replace('{history}', transcript)
        return formatted_user_message
    
    
    def make_openai_request(self, request_params:dict):
        response = self.llm_client.responses.create(
            **request_params
        )
        if response.status == 'completed':
            return response.model_dump()
        else:
            raise RuntimeError(f'Response.status is not completed! Response object below: \n\n{response}\n\n')
