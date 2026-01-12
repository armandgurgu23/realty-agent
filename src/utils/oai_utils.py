from openai import OpenAI

def make_openai_request(request_params:dict, llm_client:OpenAI) -> dict:
    response = llm_client.responses.create(
        **request_params
    )
    if response.status == 'completed':
        return response.model_dump()
    else:
        raise RuntimeError(f'Response.status is not completed! Response object below: \n\n{response}\n\n')