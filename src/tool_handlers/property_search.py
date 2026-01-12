
import time
from openai import OpenAI
from src.prompts.mock_properties import SYSTEM_PROMPT_FAKE_PROPERTIES
from src.utils.oai_utils import make_openai_request


def get_listings_for_neighbourhood(neighbourhood: str, llm_client:OpenAI):

    rendered_prompt = SYSTEM_PROMPT_FAKE_PROPERTIES.replace('{neighbourhood}', neighbourhood)

    oai_request_params = {
        'input': [
            {
                'role': 'system', 'content': rendered_prompt
            }
        ],
        'model': 'gpt-4.1-mini-2025-04-14',
        'temperature': 0.0
    }

    return make_openai_request(oai_request_params, llm_client)

def get_points_of_interest_for_listing(listing_address:str, llm_client:OpenAI):
    return f"{listing_address} has the best schools and the best grocery stores."









