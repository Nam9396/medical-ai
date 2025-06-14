import os
import time
from huggingface_hub import get_inference_endpoint, InferenceEndpointTimeoutError
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from gradio_client import Client

hf_token = os.environ["HUGGINGFACEHUB_API_TOKEN"]

endpoint_url = "https://uu7nhxp2xlel7pok.us-east-1.aws.endpoints.huggingface.cloud"

llm = HuggingFaceEndpoint(
    endpoint_url=endpoint_url,
    task="text-generation",
    max_new_tokens=1024,
    do_sample=False,
    repetition_penalty=1.03,
)

medgemma_chat_model = ChatHuggingFace(llm=llm)

medgemma_gradio_client = Client("Nam9396/medgemma-app", hf_token=hf_token)

medgemma_endpoint = get_inference_endpoint(name="medgemma-4b-it-ily", token=hf_token)


def ensure_endpoint_running(timeout: int = 420, poll_interval: int = 5):
    """
    Ensures a Hugging Face Inference Endpoint is running.
    If it's pending or scaled to zero, it waits until it's ready.

    Args:
        endpoint_name (str): Name of the endpoint.
        namespace (str): Your HF account or org name.
        timeout (int): Maximum wait time in seconds.
        poll_interval (int): Time between checks in seconds.

    Returns:
        InferenceEndpoint: Ready and running endpoint instance.

    Raises:
        TimeoutError: If the endpoint doesn't become ready in time.
    """
    start = time.time()
    endpoint = get_inference_endpoint(name="medgemma-4b-it-ily", token=hf_token)
    endpoint.resume()

    while True:
        try:
            # This refreshes the endpoint status and waits if needed
            endpoint.wait(timeout=poll_interval)
            if endpoint.status == "running" and endpoint.url:
                return endpoint
        except InferenceEndpointTimeoutError:
            # This is expected if it times out waiting for a poll_interval
            pass

        if time.time() - start > timeout:
            raise TimeoutError(f"Endpoint did not become ready within {timeout} seconds.")

        time.sleep(poll_interval)  # Wait before next check




