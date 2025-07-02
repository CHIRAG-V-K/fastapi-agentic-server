import json
import re
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from tools import wikipedia_tool, duckduckgo_tool, calendar_tool

# Load model and tokenizer once at startup
tokenizer = AutoTokenizer.from_pretrained("Groq/Llama-3-Groq-8B-Tool-Use")
model = AutoModelForCausalLM.from_pretrained("Groq/Llama-3-Groq-8B-Tool-Use")
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.float32,
    device=0 if torch.cuda.is_available() else -1
)

# Tool registry mapping tool names to functions
TOOL_REGISTRY = {
    "wikipedia_search": wikipedia_tool.func,
    "duckduckgo_search": duckduckgo_tool.func,
    "calendar_event": calendar_tool.func,
}

def parse_tool_call(output_text):
    """
    Parse a tool call from the model output.
    Adjust this function if your model outputs tool calls in a different format.
    """
    match = re.search(r"\{.*\}", output_text, re.DOTALL)
    if match:
        try:
            tool_call = json.loads(match.group(0))
            return tool_call
        except Exception:
            return None
    return None

def orchestrate_tool_call(message: str):
    """
    Orchestrate the tool calling process:
    1. Send user message to the model.
    2. Parse tool call from model output.
    3. Execute the tool if requested.
    4. Feed tool result back to the model for a final answer.
    5. Return the full interaction.
    """
    # Step 1: Get model output for the user message
    messages = [{"role": "user", "content": message}]
    output = pipe(messages, max_new_tokens=512, return_full_text=False)[0]["generated_text"]

    # Step 2: Parse tool call
    tool_call = parse_tool_call(output)
    if tool_call and "tool_name" in tool_call and "arguments" in tool_call:
        tool_name = tool_call["tool_name"]
        arguments = tool_call["arguments"]
        tool_func = TOOL_REGISTRY.get(tool_name)
        if tool_func:
            # Step 3: Execute the tool
            tool_result = tool_func(**arguments)
            # Step 4: Feed tool result back to the model
            followup = [
                {"role": "user", "content": message},
                {"role": "tool", "content": str(tool_result)}
            ]
            final_output = pipe(followup, max_new_tokens=256, return_full_text=False)[0]["generated_text"]
            return {
                "tool_call": tool_call,
                "tool_result": tool_result,
                "final_output": final_output
            }
        else:
            return {
                "error": f"Tool '{tool_name}' not found.",
                "model_output": output
            }
    else:
        # No tool call detected, just return the model output
        return {"model_output": output}