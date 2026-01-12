from openai import OpenAI
import json
from src.tool_handlers.property_search import get_properties_for_user

def parse_xml_content(xml_string:str, tag_name:str) -> str | None:
    """
    Extract the content from an XML tag in a string.
    
    Args:
        xml_string: String containing XML
        tag_name: Name of the XML tag to extract content from
    
    Returns:
        The content inside the XML tag, or None if tag not found
    """
    start_tag = f"<{tag_name}>"
    end_tag = f"</{tag_name}>"
    
    start_index = xml_string.find(start_tag)
    if start_index == -1:
        return None
    
    # Move past the opening tag
    content_start = start_index + len(start_tag)
    
    # Find the closing tag
    end_index = xml_string.find(end_tag, content_start)
    if end_index == -1:
        return None
    
    return xml_string[content_start:end_index]

class RealtyAgent(object):
    # TODO: Add a proper dataclass after.
    def __init__(self, system_prompt_template:str, user_prompt_template:str, llm_client:OpenAI):
        self.system_prompt_template = system_prompt_template
        self.user_prompt_template = user_prompt_template
        # Client + Modelling parameters.
        self.llm_client = llm_client
        self.model_snapshot = 'gpt-4.1-mini-2025-04-14'
        self.model_temperature = 0.0
        # Just for troubleshooting purposes. Remember to set False when demo is finished.
        self.debug_mode = False


    def get_agent_response(self, user_message:str, chat_history:list[dict], should_chat_end:bool):
        # print(user_message)
        # print(chat_history)
        # print(should_chat_end)
        # TODO: Fill in logic with chatbot logic here. For now echoing back the user written message.
        oai_user_message = self.prepare_oai_user_message_from_history(chat_history, user_message)

        if self.debug_mode:
            print(oai_user_message)

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

        if self.debug_mode:
            print(f'Number of outputs in first OAI request: {len(response['output'])}')
            print(response['output'])


        for curr_item in response['output']:
            if curr_item['type'] == 'message':
                agent_message, should_chat_end = self.parse_chat_message_from_output(response['output'][0])
            elif curr_item['type'] == 'function_call' and curr_item['name'] == 'get_properties_for_user':
                function_arguments = json.loads(curr_item['arguments'])
                available_listings = get_properties_for_user(**function_arguments)
                updated_oai_messages = self.update_messages_with_tool_information(
                    tool_input=curr_item,
                    tool_output={
                        "type": "function_call_output",
                        "call_id": curr_item['call_id'],
                        "output": available_listings
                    },
                    oai_messages=oai_request_params['input']
                )
                # Now carry out the OAI request to generate response based on tool call output.
                oai_request_params["input"] = updated_oai_messages
                new_response = self.make_openai_request(oai_request_params)
                if self.debug_mode:
                    print(f'Number of outputs in second OAI request: {len(new_response['output'])}')
                    print(new_response['output'])
                agent_message, should_chat_end = self.parse_chat_message_from_output(new_response['output'][0])
            else:
                breakpoint()
                if self.debug_mode:
                    print('Unexpected output item type! Inspect it!')

        return f"{agent_message}", should_chat_end
    
    def update_messages_with_tool_information(self, tool_input:dict, tool_output:dict, oai_messages):
        user_message = oai_messages[-1]['content']
        transcript_text = parse_xml_content(user_message, 'history')
        transcript_text += f"BOT: {tool_input}\nBOT:{tool_output}\n"
        oai_messages[-1]['content'] = transcript_text
        return oai_messages
    
    def parse_chat_message_from_output(self, output_message):
        try:
            chat_response_json = json.loads(output_message['content'][0]['text'])
        except:
            breakpoint()
        return chat_response_json['msg'], chat_response_json['should_chat_end']
    
    
    def prepare_tool_definitions(self):
        return [
            {
                'type': "function",
                'name': 'get_properties_for_user',
                "description": "Use this tool to find properties for sale or for rent when the user mentions that they are interested to move.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "neighbourhood": {
                            "type": "string",
                            "description": "A neighbourhood where the user may be interested to move in to."
                        }
                    },
                    "required": ["neighbourhood"]
                }
            }
        ]
    
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
            transcript = '\n'.join([f"{curr_turn['role']}: {curr_turn['content']}" for curr_turn in chat_history])
            # Make sure to add the incoming current message as well.
            transcript += f'\nUSER: {user_message}'

        formatted_user_message = self.user_prompt_template.replace('{history}', transcript)
        # NOTE: In a production setting a multi-turn transcript can get quite lengthy in terms of input tokens,
        # So you would likely want to apply some transcript context management compression here if
        # we get close to eating up the context window of the LLM. For now I'm omitting handling this situation.
        return formatted_user_message
    
    
    def make_openai_request(self, request_params:dict):
        response = self.llm_client.responses.create(
            **request_params
        )
        if response.status == 'completed':
            return response.model_dump()
        else:
            raise RuntimeError(f'Response.status is not completed! Response object below: \n\n{response}\n\n')
