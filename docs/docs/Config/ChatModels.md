# Chat Models

## Supported Language Models
### Providers
**1\. OpenAI** (Default)
- Models: `gpt-4o` (default), `gpt-4o-mini`

**2\. Google Gemini**
- Models: `gemini-2.0-flash-exp`, `gemini-2.0-flash-lite`

**3\. Anthropic**
- Models: `claude-3-5-haiku-20241022`, `claude-3-haiku-20240307`


## Taskgraph 
- **Note:** Taskgraph construction with different models isn't supported at the time, only OpenAI can be used. Feature is planned to be implemented in the future.

## Running the Bot

### OpenAI
- Add your `OPEN_API_KEY` to the `.env` file
- Example usage:
    ```
    python run.py --input-dir ./examples/customer_service --model gpt-4o-mini --llm-provider openai
    ```
    
### Google Gemini
- Add your `GOOGLE_API_KEY`  and `GEMINI_API_KEY` to the `.env` file
    - Note: Both API keys should be the same
- Example usage:
     ```
    python run.py --input-dir ./examples/customer_service --model gemini-2.0-flash-lite --llm-provider gemini
    ```

### Anthropic
- Add your `ANTHROPIC_API_KEY` to .env
- Example usage:
    ```
    python run.py --input-dir ./examples/customer_service --model claude-3-5-haiku-20241022 --llm-provider anthropic
    ```



## Sample conversation
To run the bot, use the following command:
  ```
python run.py --input-dir ./examples/shopify --model claude-3-5-haiku-20241022 --llm-provider anthropic
  ```

### Example Output

