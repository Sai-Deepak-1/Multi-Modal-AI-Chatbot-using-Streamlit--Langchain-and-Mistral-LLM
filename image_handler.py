from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
import base64

def convert_image_to_base64(image_bytes):
    encoded_string = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"


def handle_image(image_bytes, user_message):
    chat_handler = Llava15ChatHandler(
        clip_model_path="models\llava\mmproj-model-f16.gguf"
    )
    llm = Llama(
        model_path="models\llava\ggml-model-q5_k.gguf",
        chat_handler=chat_handler,
        n_ctx=2048,  # n_ctx should be increased to accomodate the image embedding
        logits_all=True,  # needed to make llava work
    )
    image_base64 = convert_image_to_base64(image_bytes)
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": "Please Explain about this Image in Detail ",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_base64},
                    },
                    {"type": "text", "text": user_message},
                ],
            },
        ]
    )
    print(output)
    return output["choices"][0]["message"]["content"]
